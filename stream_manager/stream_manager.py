import numpy as np
import requests
import threading
import logging
from time import sleep
import cv2


def make_analysed_url(source_url):
    return source_url + "_analysed"


logger = logging.getLogger(__name__)
class StreamManager(threading.Thread):
    def __init__(self):
        # TODO: trzymać w bazie danych, ale pewnie nie bedzie sie chcialo XD
        super().__init__()
        self.source_urls = []
        self.base_url = 'rtmp://localhost/live/'
        self.analyzer_url = 'http://127.0.0.1:5000/'
        self.interval = 10

    def update_urls(self):
        for source_url in self.source_urls:
            if not self.check_url(source_url):
                self.source_urls.remove(source_url)
            elif not self.check_url(make_analysed_url(source_url)):
                self.publish_source_url(source_url)

    def check_url(self, url):
        try:
            logger.info(f"Stream {url} is available")
            cv2.VideoCapture(url)
            return True
        except:
            logger.warning(f"Stream {url} not available")
            return False

    def publish_source_url(self, source_url):
        requests.post(self.analyzer_url + 'analyze', data={'url': source_url})
        pass

    def submit_stream(self):
        seed = np.random.randint(999999)
        url = f'{self.base_url}{seed}'
        # TODO: to cos nie dziala, cos z watkami sie pewnie pieprzy, cza naprawic
        self.source_urls.append(url)
        # requests.post(self.analyzer_url+'analyze', data={'url': url})
        return url

    def run(self):
        while 1:
            print('updating')
            self.update_urls()
            sleep(self.interval)
