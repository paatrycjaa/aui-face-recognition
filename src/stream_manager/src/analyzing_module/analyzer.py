import copy
import datetime
import json
import time
import numpy as np
import pika
import threading
import cv2
from analyzing_module.facedetection import FaceDetection
import logging
from celery import Celery
from analyzing_module.conf_parser import ConfParser
import requests

BROKER_URL = '192.168.49.2'
BROKER_PORT = 30762

app = Celery('analyzer', broker=f'pyamqp://guest@{BROKER_URL}:{BROKER_PORT}//', backend='rpc://')

FPS = 30
DELAY = 0.5

logger = logging.getLogger(__name__)
CONF_PATH = 'analyzing_module/config.conf'


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
        self.model_parameters = ConfParser(CONF_PATH)
        self.model = FaceDetection(opencv=self.model_parameters['opencv'], identification=self.model_parameters['identification'],
                            scaleFactor=self.model_parameters['scaleFactor'], minNeighbours = self.model_parameters['minNeighbours'])

        params = pika.ConnectionParameters(host=self.broker_url, port=BROKER_PORT)
        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=source_url)
        self.frame = None
        self.reading = True
        self.frame_ready = False
        self.stats = []

    def run(self):
        i = 0
        self.read_continuous()
        while self.reading:
            if not self.frame_ready or self.frame.shape[0] < 10:
                time.sleep(0.01)
                continue
            start_time = datetime.datetime.now()
            # cv2.imshow('frame', self.frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            result = DetectionResult(src_url=self.source_url, time=start_time, results=self.model.perform_face_detection(self.frame))
            self.channel.basic_publish(exchange='', routing_key=self.source_url, body=str(result))

            self.stats.append({'time': str(datetime.datetime.now()),
                               'process_time': (datetime.datetime.now() - start_time).microseconds,
                               'face_count': len(result.results),
                               'resolution': (self.frame.shape[0], self.frame.shape[1])})
            i += 1
            if i == 300:
                now = datetime.datetime.now()
                filename = f'log-{self.source_url.split("/")[-1]}-{now.hour}:{now.minute}:{now.second}.txt'
                logger.warning(f"saving logs to {filename}")
                with open(filename, 'w+') as log_file:
                    json.dump(self.stats, log_file, indent=2)
                self.stats = []
                i = 0
            self.frame_ready = False

    def read_continuous(self):
        def read():
            while True:
                # while cap.isOpened():
                ret, frame = self.cap.read()
                self.reading = ret
                if not ret:
                    print("frame read failed")
                    break
                if not self.frame_ready:
                    self.frame = frame
                    self.frame_ready = True
                else:
                    pass
                    #time.sleep(0.01)
        threading.Thread(target=read, daemon=True).start()


@app.task
def analyze(source_url, broker_url, broker_port):
    """
    performs analysis on stream available under source_url and sends results to broker_url
    Args:
        self:
        source_url:
        broker_url:
        broker_port:

    Returns:

    """
    logger.error(source_url)
    analyzer = Analyzer(source_url=source_url)
    analyzer.broker_url = broker_url
    analyzer.broker_port = broker_port
    analyzer.run()


if __name__ == "__main__":
    result = analyze(source_url='rtmp://192.168.49.2:30000/live/1',
            broker_url='192.168.49.2',
            broker_port=30762)
    while True:
        time.sleep(1)
        print(result.state)
    print("nic")
