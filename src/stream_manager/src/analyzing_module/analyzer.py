import datetime
import time

import pika
import threading
import cv2
from analyzing_module.facedetection import FaceDetection
import logging
from celery import Celery

BROKER_URL = '192.168.49.2'
BROKER_PORT = 30762

app = Celery('analyzer', broker=f'pyamqp://guest@{BROKER_URL}:{BROKER_PORT}//', backend='rpc://')

FPS = 30
DELAY = 0.5

logger = logging.getLogger(__name__)


class DetectionResult:
    def __init__(self, src_url:str = None, time:datetime.datetime = None, results: list = None):
        self.src_url = src_url
        self.timestamp = time
        self.results = results
        self.delimiter = ';'

    def __str__(self):
        return self.delimiter.join([self.src_url, str(self.timestamp), str(self.results)])

    def decode(self, string: str):
        string = string.split(self.delimiter)
        self.src_url = string[0]
        self.timestamp = datetime.datetime.fromisoformat(string[1])
        self.results = eval(string[2])


class Analyzer(threading.Thread):
    def __init__(self, source_url):
        super().__init__()
        self.source_url = source_url
        self.broker_url = BROKER_URL
        self.broker_port = BROKER_PORT
        self.cap = cv2.VideoCapture(self.source_url)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.model = FaceDetection(opencv=True, identification=False)

        params = pika.ConnectionParameters(host=self.broker_url, port=BROKER_PORT)
        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=source_url)

    def run(self, worker=None):
        i = 0
        missed_frames = 0
        total_duration = datetime.timedelta(seconds=0)
        while True:
            if missed_frames == 30:
                break
            # while cap.isOpened():
            ret, frame = self.cap.read()
            time = datetime.datetime.now()
            if not ret:
                print("frame read failed")
                missed_frames += 1
                break
            missed_frames = 0
            result = DetectionResult(src_url=self.source_url, time=time, results=self.model.find_faces(frame))
            total_duration += datetime.datetime.now()-time
            self.channel.basic_publish(exchange='', routing_key=self.source_url, body=str(result))
            i += 1
            if i == 30:
                logger.warning(f'analyzed 30 frames with avg analysis time {total_duration/30}')
                total_duration = datetime.timedelta(seconds=0)
                i = 0
                if worker is not None:
                    worker.update_state(state=f'{str(datetime.datetime.now())}')


@app.task(bind=True)
def analyze(self, source_url, broker_url, broker_port):
    """
    performs analysis on stream available under source_url and sends results to broker_url
    Args:
        self:
        source_url:
        broker_url:
        broker_port:

    Returns:

    """
    analyzer = Analyzer(source_url=source_url)
    analyzer.broker_url = broker_url
    analyzer.broker_port = broker_port
    analyzer.run(self)


if __name__ == "__main__":
    result = analyze.delay(source_url='rtmp://192.168.49.2:30000/live/1',
            broker_url='192.168.49.2',
            broker_port=30762)
    while True:
        time.sleep(1)
        print(result.state)
    print("nic")
