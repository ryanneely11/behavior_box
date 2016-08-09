import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('/home/pi/Desktop/output.avi',fourcc, 60.0, (640,480))

start_time = time.time()

while (time.time() - start_time) < 20.0:
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()