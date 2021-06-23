import datetime

import random
from typing import List

import requests
import threading
import logging
from time import sleep
import librtmp
from analyzing_module import analyzer


def make_analysed_url(source_url):
    return source_url + "_a"


logger = logging.getLogger(__name__)


class StreamManager:
    class StreamHandler:
        def __init__(self, source_url, worker, last_online=None, last_output_online=None):
            self.source_url = source_url
            self.worker = worker
            self.last_online = last_online or datetime.datetime.now()
            self.last_output_online = last_output_online
            self.analysis_requested = datetime.datetime.now()
            self.last_analysis = None

        def __dict__(self):
            return {
                'source_url': self.source_url,
                'last_online': str(self.last_online),
                'last_output_online': str(self.last_output_online),
                'analysis_requested': str(self.analysis_requested),
                'last_analysis': self.last_analysis
            }

    def __init__(self):
        self.stream_handlers: List[StreamManager.StreamHandler] = []
        self.rtmp_url = 'rtmp://localhost/live/'
        self.analyzer_url = 'http://127.0.0.1:5000/'
        self.broker_url = '192.168.49.2'
        self.drawer_url = 'http://127.0.0.1:5004/'
        self.manager_url = 'http://localhost:5001'
        self.broker_port = 30762
        self.interval = 5
        self.remove_after = 20
        self.update_worker = None
        self.consumer_worker = None
        self.do_update = True
        self.analysis_config = {
            'opencv': True,
            'identification': True,
            'scaleFactor': 1.05,
            'minNeighbours': 6
        }


    def get_handled_urls(self):
        return [handler.source_url for handler in self.stream_handlers]

    def get_handler(self, url):
        try:
            return [handler for handler in self.stream_handlers if handler.source_url == url][0]
        except IndexError:
            logger.warning(f"trying to get non existing handler {url}")

    def update_urls(self):
        for source_url in self.get_handled_urls():
            handler = self.get_handler(source_url)
            if self.check_url(source_url):
                handler.last_online = datetime.datetime.now()
                if self.check_url(make_analysed_url(source_url)):
                    handler.last_output_online = datetime.datetime.now()
                else:
                    self.request_draw(source_url)
            else:
                if datetime.datetime.now() - handler.last_online > \
                        datetime.timedelta(seconds=self.remove_after):
                    self._remove_stream_url(source_url)

    def get_handlers(self):
        return [handler.__dict__() for handler in self.stream_handlers]

    def heartbeat_analysis(self, url):
        url = f'{self.rtmp_url}{url}'
        self.get_handler(url).last_analysis = datetime.datetime.now()

    def _add_stream_url(self, url, worker):
        self.stream_handlers.append(StreamManager.StreamHandler(url, worker))

    def _remove_stream_url(self, url):
        self.stream_handlers = list(filter(lambda h: h.source_url != url, self.stream_handlers))

    def check_url(self, url):
        # TODO: asyncio????
        try:
            conn = librtmp.RTMP(url, timeout=1)
            conn.connect()
            stream = conn.create_stream()
            data = stream.read(1)
            if not data:
                logger.warning(f"unavailable stream {url}")
                return False
        except librtmp.exceptions.RTMPError as e:
            logger.warning(f"unavailable stream {url}")
            return False
        logger.warning(f"available stream {url}")
        return True

    def request_analysis(self, source_url):
        handler = self.get_handler(source_url)
        handler.worker.revoke(terminate=True)
        handler.worker = analyzer.analyze.delay(source_url=source_url,
                                                broker_url=self.broker_url,
                                                broker_port=self.broker_port)
        handler.analysis_requested = datetime.datetime.now()

    def request_draw(self, source_url):
        try:
            requests.post(self.drawer_url + 'draw',
                          data={'url': source_url,
                                'output_url': make_analysed_url(source_url)})
        except:
            logger.warning("Drawer API offline")
        pass

    def submit_stream(self):
        seed = random.randint(0, 1000)
        seed = 1
        url = f'{self.rtmp_url}{seed}'

        while url in self.get_handled_urls():
            seed = random.randint(0, 1000)
            url = f'{self.rtmp_url}{seed}'
        worker = analyzer.analyze.delay(source_url=url,
                                        broker_url=self.broker_url,
                                        broker_port=self.broker_port,
                                        manager_url=self.manager_url,
                                        analysis_config=self.analysis_config
                                        )
        self._add_stream_url(url, worker)
        return seed

    def run(self):
        while self.do_update:
            self.check_drawer_status()
            self.update_urls()
            sleep(self.interval)

    def check_analyzer_status(self):
        try:
            result = requests.get(self.analyzer_url + 'status')
            logger.info("Analyzer API online")
        except:
            logger.warning("Analyzer API offline")

    def check_drawer_status(self):
        try:
            result = requests.get(self.drawer_url + 'status')
            logger.info("Drawer API online")
        except:
            logger.warning("Drawer API offline")

    def start(self):
        self.update_worker = threading.Thread(target=self.run, daemon=True)
        self.update_worker.start()
        # self.consumer_worker = threading.Thread(target=self.consume_results, daemon=True)
        # self.consumer_worker.start()

    def __del__(self):
        self.do_update = False
