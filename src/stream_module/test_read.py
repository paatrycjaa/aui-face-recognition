import datetime
import cv2
import time

cap = cv2.VideoCapture('rtmp://192.168.49.2:30000/live/1')

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    time.sleep(1/30)
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()