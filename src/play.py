import datetime
import time

import cv2

FPS = 30
if __name__ == "__main__":
    cap = cv2.VideoCapture('output.mp4')

    while (cap.isOpened()):
        start_time = datetime.datetime.now()
        ret, frame = cap.read()
        if ret == True:
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
        time.sleep(max(1/FPS - (datetime.datetime.now()-start_time).microseconds/1000000, 0))

    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()