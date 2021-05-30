import datetime

import numpy as np
import requests
import threading
import logging
from time import sleep
import cv2
import redis
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
            self.db = redis.Redis('localhost', port=6379, db=0)
        else:
            self.db = None
        self.base_url = 'rtmp://localhost/live/'
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
            return list(map(lambda url: url.decode('utf-8'), self.db.scan_iter()))
        else:
            return self.source_urls

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
                return False
        except librtmp.exceptions.RTMPError as e:
            return False
        return True

    def publish_source_url(self, source_url):
        try:
            requests.post(self.analyzer_url + 'analyze',
                          data={'url': source_url,
                                'url_analyzed': make_analysed_url(source_url)})
        except:
            logger.warning("Analyzer API off line")
        pass

    def submit_stream(self):
        seed = np.random.randint(1000)
        seed = 1
        url = f'{self.base_url}{seed}'
        while url in self.get_stream_urls():
            seed = np.random.randint(1000)
            url = f'{self.base_url}{seed}'
        # TODO: to cos nie dziala, cos z watkami sie pewnie pieprzy, cza naprawic
        self._add_stream_url(url)
        # requests.post(self.analyzer_url+'analyze', data={'url': url})
        return url

    def run(self):
        while self.do_update:
            print('updating')
            self.update_urls()
            sleep(self.interval)

    def start(self):
        self.update_worker = threading.Thread(target=self.run)
        self.update_worker.start()

    def __del__(self):
        self.do_update = False

