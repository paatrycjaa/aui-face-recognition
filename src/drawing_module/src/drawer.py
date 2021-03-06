import datetime
import logging
import os
import subprocess
import time

import pika
import numpy as np
import threading
import cv2
from frame_buffer import FrameBuffer
from time_series import TimeSeries
import json

FPS = 30
DELAY = 1
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


class Drawer(threading.Thread):

    def __init__(self, source_url, output_url):
        super().__init__()
        self.source_url = source_url
        self.output_url = output_url
        self.broker_url = '192.168.49.2'
        self.broker_port = 30762
        self.cap = cv2.VideoCapture(self.source_url)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.buffer = FrameBuffer(100, self.height, self.width, 3)
        self.results = TimeSeries()
        self.frame = None
        self.frame_ready = False
        self.reading = True
        self.stats = []

    def draw_bounding_boxes(self, frame, results):
        if results is None:
            return
        for result in results:
            x1, y1, width, height, name = result
            x2 = x1 + width
            y2 = y1 + height
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255))
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (x1, y1), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    def process(self, frame: np.array):
        self.buffer.update(frame)
        result = self.results[datetime.datetime.now()-datetime.timedelta(seconds=DELAY)]
        if result is None:
            return frame, 0
        frame = self.buffer[int(DELAY*FPS)]
        self.draw_bounding_boxes(frame, result)
        return frame, len(result)

    def run(self):
        missed_frames = 0
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(self.width, self.height),
                   '-r', str(self.fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   f'{self.output_url}']

        # using subprocess and pipe to fetch frame data
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        self.read_continuous()
        i = 0
        while self.reading:
            if not self.frame_ready:
                time.sleep(0.01)
                continue
            start_time = datetime.datetime.now()
            result, face_count = self.process(self.frame)
            self.stats.append({'time': str(datetime.datetime.now()),
                               'process_time': (datetime.datetime.now() - start_time).microseconds,
                               'face_count': face_count,
                               'resolution': (self.frame.shape[0], self.frame.shape[1])})
            i += 1
            if i == 300:
                now = datetime.datetime.now()
                if not os.path.isdir('logs'):
                    os.mkdir('logs')
                filename = f'logs/log-{self.source_url.split("/")[-1]}-{now.hour}:{now.minute}:{now.second}.txt'
                logger.warning(f"saving logs to {filename}")
                with open(filename, 'w+') as log_file:
                    json.dump(self.stats, log_file, indent=2)
                self.stats = []
                i = 0
            p.stdin.write(result.tobytes())
            self.frame_ready = False
        p.kill()

    def consume_results(self):
        params = pika.ConnectionParameters(host=self.broker_url, port=self.broker_port)
        connection = pika.BlockingConnection(parameters=params)
        channel = connection.channel()
        channel.queue_declare(queue=self.source_url)

        def callback(ch, method, properties, body):
            body = body.decode('utf-8').split(';')
            timestamp = datetime.datetime.fromisoformat(body[1])
            results = eval(body[2])
            self.results.update(results, timestamp)
            # print(f"{self.source_url} sent result for {timestamp} at {datetime.datetime.now()} delta {(datetime.datetime.now() - timestamp).microseconds})")
            # logger.warning(body)

        channel.basic_consume(queue=self.source_url, auto_ack=True, on_message_callback=callback)
        channel.start_consuming()

    def start_consume(self):
        self.consumer_thread = threading.Thread(target=self.consume_results)
        self.consumer_thread.start()

    def read_continuous(self):
        def read():
            while True:
                # while cap.isOpened():
                ret, frame = self.cap.read()
                self.reading = ret
                if not ret:
                    print("frame read failed")
                    break
                self.frame = frame
                self.frame_ready = True
        threading.Thread(target=read, daemon=True).start()

if __name__ == "__main__":
    analyzer = Drawer(source_url="rtmp://192.168.49.2:30000/live/1", output_url="rtmp://192.168.49.2:30000/live/1_a")
    analyzer.start_consume()
    print('nicnic')
    analyzer.run()
    # analyzer.join()
    print("nic")
    # time.sleep(10000)
