import cv2
import requests
import subprocess


class Streamer:
    def __init__(self, manager_url, capture_device=0, display=False):
        self.manager_url = manager_url
        self.stream_url = None
        self.cap = cv2.VideoCapture(capture_device)
        self.stream_url = self.get_stream_url()
        self.display = display

    def get_stream_url(self):
        response = requests.post(self.manager_url + "/streams")
        return response.content.decode('utf-8').strip().replace('"', '')

    def stream(self):
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


s = Streamer("http://localhost:5001", display=True)
s.stream()
