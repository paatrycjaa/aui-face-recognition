import datetime
import subprocess

import numpy as np
import threading
import cv2
from facedetection import FaceDetection
from frame_buffer import FrameBuffer
from time_series import TimeSeries

FPS = 30
DELAY = 0.5


class Analyzer(threading.Thread):
    class Worker:
        def __init__(self, frame=None):
            super().__init__()
            self.thread = None
            self.frame = frame
            self.running = False
            self.finished = None
            self.model = FaceDetection(opencv=True, identification=False)
            self.results = TimeSeries()

        def set_frame(self, frame):
            self.frame = frame

        def run(self):
            self.results.update(self.model.find_faces(self.frame))
            self.finished = datetime.datetime.now()

        def is_running(self):
            if self.thread is None:
                return False
            return self.thread.is_alive()

        def start(self):
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def __init__(self, url, analyzed_url):
        super().__init__()
        self.url = url
        self.analyzed_url = analyzed_url
        self.cap = cv2.VideoCapture(self.url)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.model = FaceDetection(opencv=True, identification=False)
        self.worker = Analyzer.Worker()
        self.buffer = FrameBuffer(100, self.height, self.width, 3)

    def process(self, frame: np.array):
        self.buffer.update(frame)
        if not self.worker.is_running():
            self.worker.set_frame(frame)
            self.worker.start()
        result = self.worker.results[datetime.datetime.now()-datetime.timedelta(seconds=DELAY)]
        # return self.model.extract_face(self.buffer[int(DELAY*FPS)])
        frame = self.buffer[int(DELAY*FPS)]
        self.model.draw_bounding_boxes(frame, result)
        return frame
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
                   f'{self.analyzed_url}']

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
        p.kill()


if __name__ == "__main__":
    analyzer = Analyzer(url='rtmp://localhost/live/1')
    analyzer.run()
    # analyzer.join()
    print("nic")
    # time.sleep(10000)
