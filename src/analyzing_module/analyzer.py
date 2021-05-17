import subprocess
import time

import numpy as np
import threading
import cv2
from facedetection import FaceDetection
from src.analyzing_module.frame_buffer import FrameBuffer

class Analyzer(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.model = FaceDetection(opencv=True, identification=False)
        self.buffer = FrameBuffer(100, self.height, self.width, 3)

    def process(self, frame: np.array):
        self.buffer.update(frame)
        return self.model.extract_face(self.buffer[0])
        #return (self.buffer[self.current_element] + self.buffer[self.current_element-30])/2

    def run(self):
        # time.sleep(1000)
        # return

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
                   f'{self.url}_analyzed']

        # using subprocess and pipe to fetch frame data
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        while True:
            # while cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("frame read failed")
                break

            # YOUR CODE FOR PROCESSING FRAME HERE

            # write to pipe
            p.stdin.write(self.process(frame).tobytes())


if __name__ == "__main__":
    analyzer = Analyzer(url='rtmp://localhost/live/1')
    analyzer.run()
    # analyzer.join()
    print("nic")
    # time.sleep(10000)
