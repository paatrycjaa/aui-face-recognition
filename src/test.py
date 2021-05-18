import threading
import time


class Test:
    def __init__(self):
        self.thread = None
    def run(self):
        time.sleep(2)
        print("pindol")

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

t = Test()
t.start()
time.sleep(5)
t.start()