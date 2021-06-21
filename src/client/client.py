import datetime
import time

import requests
import json
import cv2
import enum
import numpy as np
import threading
import math


class StreamState(enum.Enum):
    ONLINE = 1
    OFFLINE = 0


UPDATE_PERIOD = 5


class StreamCapture:
    def __init__(self, url, tag=None):
        self.url = url
        self.thread = None
        self.frame = np.zeros((2,2,3), dtype=np.uint8)
        self.consume = True
        self.cap = cv2.VideoCapture(url)
        self.tag = tag

    def capture(self):
        ret, self.frame = self.cap.read()
        return ret

    def run(self):
        while self.consume:
            ret = self.capture()
            if not ret:
                break

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()


def make_analysed_url(source_url):
    return source_url + "_a"


class Client:
    def __init__(self, manager_url):
        self.manager_url = manager_url
        self.streams = []
        self.last_update = None
        self.caps = []
        self.height = 1080
        self.width = 1920
        self.fps = 30
        self.update_worker = None
        self.run_update_worker = True

    def get_streams(self):
        response = requests.get(self.manager_url+"/streams")
        response = json.loads(response.content)
        result = []
        for stream in response:
            status = StreamState.ONLINE if stream['last_output_online'] != 'None' and \
                datetime.datetime.fromisoformat(stream['last_online']) -\
                datetime.datetime.fromisoformat(stream['last_output_online']) < \
                datetime.timedelta(seconds=5) else StreamState.OFFLINE
            result.append((
                stream['source_url'],
                make_analysed_url(stream['source_url']),
                status
            ))
        return result

    def update_caps(self):
        streams = self.get_streams()
        source_urls = [stream[0] for stream in streams if stream[2] == StreamState.OFFLINE]
        analyzed_urls = [stream[1] for stream in streams if stream[2] == StreamState.ONLINE]
        for cap in self.caps:
            if cap.url not in source_urls and cap.url not in analyzed_urls:
                cap.consume = False
        self.caps = list(filter(lambda cap: cap.consume, self.caps))

        consumed_urls = [cap.url for cap in self.caps]
        for source_url in source_urls:
            if source_url not in consumed_urls:
                cap = StreamCapture(source_url, tag="SOURCE")
                cap.start()
                self.caps.append(cap)
        for analyzed_url in analyzed_urls:
            if analyzed_url not in consumed_urls:
                cap = StreamCapture(analyzed_url, tag="SOURCE")
                cap.start()
                self.caps.append(cap)

    def run(self):
        def run_update_caps():
            while self.run_update_worker:
                self.update_caps()
                time.sleep(UPDATE_PERIOD)
        self.update_worker = threading.Thread(target=run_update_caps)
        self.update_worker.start()
        while True:
            display = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            size = math.ceil(math.sqrt(len(self.caps)))
            if size != 0:
                block_width = self.width // size
                block_height = self.height // size
                for i, cap in enumerate(self.caps):
                    if cap.frame is None:
                        continue
                    coord_y = i//size
                    coord_x = i - size * coord_y
                    frame_height = cap.frame.shape[0]
                    frame_width = cap.frame.shape[1]
                    scale_factor = min(block_height/frame_height, block_width/frame_width)
                    frame_height = int(frame_height * scale_factor)
                    frame_width = int(frame_width * scale_factor)
                    frame = cv2.resize(cap.frame, (frame_width, frame_height))
                    pad_height = (block_height - frame_height)//2
                    pad_width = (block_width - frame_width) // 2
                    if frame.shape[0] == block_height and frame.shape[1] == block_width:
                        display[coord_y*block_height + pad_height:coord_y*block_height + pad_height + frame_height,
                              coord_x*block_width + pad_width: coord_x*block_width + pad_width + frame_width] = frame
            cv2.imshow("frame", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def __del__(self):
        for cap in self.caps:
            cap.consume = False
        self.run_update_worker = False

if __name__ == '__main__':
    client = Client('http://127.0.0.1:5001/')
    client.update_caps()
    client.run()

