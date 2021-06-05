import datetime
import time

import cv2
import requests
import subprocess
import sys
from typing import Union


class Streamer:
    def __init__(self, manager_url, capture_device: Union[int, str] = 0, display=False):
        self.manager_url = manager_url
        self.stream_url = None
        self.capture_device = capture_device
        self.cap = cv2.VideoCapture(capture_device)
        self.rtmp_url = "rtmp://192.168.49.2:30000/live/"
        self.stream_url = self.get_stream_url()
        self.display = display

    def get_stream_url(self):
        response = requests.post(self.manager_url + "/streams")
        sub_url = response.content.decode('utf-8').strip().replace('"', '')
        return self.rtmp_url + sub_url

    def stream(self):
        if isinstance(self.capture_device, int):
            self.stream_live()
        else:
            self.stream_file()

    def stream_live(self):
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # command and params for ffmpeg
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(width, height),
                   '-r', str(fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   self.stream_url]

        # using subprocess and pipe to fetch frame data
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        print(f"streaming to {self.stream_url}")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("frame read failed")
                break
            p.stdin.write(frame.tobytes())
            if self.display:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    def stream_file(self):
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        fps = 30
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # command and params for ffmpeg
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(width, height),
                   '-r', str(fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   self.stream_url]
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        print(f"streaming file {self.capture_device} to {self.stream_url}")
        while True:
            start_time = datetime.datetime.now()
            ret, frame = self.cap.read()
            if not ret:
                self.cap = cv2.VideoCapture(self.capture_device)
                print("frame read failed")
                continue
                # break
            p.stdin.write(frame.tobytes())
            if self.display:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(max(1 / fps - (datetime.datetime.now() - start_time).microseconds / 1000000, 0))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '../output.mp4'
    s = Streamer("http://0.0.0.0:5001/", display=True, capture_device=filename)
    s.stream()
#s.stream_file('../output.mp4')
