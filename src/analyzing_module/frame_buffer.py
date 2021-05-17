import numpy as np


class FrameBuffer:
    def __init__(self, size, height=720, width=1280, colors=3):
        self.buffer = np.zeros((size, height, width, colors), dtype=np.uint8)
        self.pointer = 0
        self.buffer_size = size

    def update(self, frame):
        self.buffer[self.pointer, :, :, :] = frame
        self.pointer += 1
        if self.pointer >= self.buffer_size:
            self.pointer = 0

    def get(self, frames_ago):
        if frames_ago > self.buffer_size:
            raise ValueError(f"Can only return last {self.buffer_size} frames")
        return self.buffer[self.pointer-frames_ago]