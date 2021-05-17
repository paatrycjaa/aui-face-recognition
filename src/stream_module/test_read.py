import datetime

import numpy as np
import cv2

time = datetime.datetime.now()

cap = cv2.VideoCapture('rtmp://localhost/live/2', timeout=2)
print(datetime.datetime.now()-time)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()