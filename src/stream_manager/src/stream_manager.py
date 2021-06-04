import datetime

import random
import requests
import threading
import logging
from time import sleep
import librtmp
import copy


def make_analysed_url(source_url):
    return source_url + "_a"

logger = logging.getLogger(__name__)


class StreamManager:
    def __init__(self, use_db=False):
        # TODO: trzymać w bazie danych, ale pewnie nie bedzie sie chcialo XD
        self.source_urls = {}
        self.analyzed_urls = {}
        self.use_db = use_db
        if use_db:
            pass
            # self.db = redis.Redis('localhost', port=6379, db=0)
        else:
            self.db = None
        self.rtmp_url = 'rtmp://localhost/live/'
        self.analyzer_url = 'http://127.0.0.1:5000/'
        self.interval = 5
        self.remove_after = 20
        self.update_worker = None
        self.do_update = True

    @staticmethod
    def create_url_status(last_online, last_analysis=None):
        return {
            'last_online': last_online,
            'last_analysis': last_analysis
        }

    def update_urls(self):
        urls = self.db.scan_iter() if self.use_db else copy.deepcopy(self.source_urls)
        for source_url in urls:
            if self.check_url(source_url):
                self.source_urls[source_url]['last_online'] = datetime.datetime.now()
                if self.check_url(make_analysed_url(source_url)):
                    self.source_urls[source_url]['last_analysis'] = datetime.datetime.now()
                else:
                    self.publish_source_url(source_url)

            else:
                if datetime.datetime.now()-self.source_urls[source_url]['last_online'] > \
                        datetime.timedelta(seconds=self.remove_after):
                    self._remove_stream_url(source_url)

    def get_stream_urls(self):
        if self.use_db:
            return list(map(lambda url: url.decode('utf-8').split('/')[-1], self.db.scan_iter()))
        else:
            return {key.split('/')[-1]: data for key, data in self.source_urls.items()}

    def _add_stream_url(self, url):
        if self.use_db:
            self.db.append(url, self.create_url_status(datetime.datetime.now()))
        else:
            self.source_urls[url] = self.create_url_status(datetime.datetime.now())

    def _remove_stream_url(self, url):
        if self.use_db:
            self.db.delete(url)
        else:
            pass
            self.source_urls.pop(url)

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
        logger.info(f"available stream {url}")
        return True

    def publish_source_url(self, source_url):
        try:
            requests.post(self.analyzer_url + 'analyze',
                          data={'url': source_url,
                                'url_analyzed': make_analysed_url(source_url)})
        except:
            logger.warning("Analyzer API offline")
        pass

    def check_analyzer_status(self):
        try:
            result = requests.get(self.analyzer_url + 'status')
            logger.info("Analyzer API online")
        except:
            logger.warning("Analyzer API offline")

    def submit_stream(self):
        seed = random.randint(0, 1000)
        seed = 1
        url = f'{self.rtmp_url}{seed}'
        while url in self.source_urls:
            seed = random.randint(0, 1000)
            url = f'{self.rtmp_url}{seed}'
        # TODO: to cos nie dziala, cos z watkami sie pewnie pieprzy, cza naprawic
        self._add_stream_url(url)
        # requests.post(self.analyzer_url+'analyze', data={'url': url})
        return seed

    def run(self):
        while self.do_update:
            self.check_analyzer_status()
            self.update_urls()
            sleep(self.interval)

    def start(self):
        self.update_worker = threading.Thread(target=self.run, daemon=True)
        self.update_worker.start()

    def __del__(self):
        self.do_update = False

