# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
import RPi.GPIO as pi

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output video file")
ap.add_argument("-f", "--fps", type=int, default=32,
	help="FPS of output video")
ap.add_argument("-c", "--codec", type=str, default="MJPG",
	help="codec of output video")
ap.add_argument("-a", "--animal", type=str, default="AnimalX",
	help="name of animal being recorded")
ap.add_argument("-s", "--session", type=str, default="Day0",
	help="Name of recording session")
args = vars(ap.parse_args())

##global vars for I/O ports
SESSION_START = 18
NEW_TRIAL = 19

##set up IO
print("[INFO] initializing I/O")
pi.setmode(pi.BCM)
pi.setup(SESSION_START, pi.IN)
pi.setup(NEW_TRIAL, pi.OUT)
trial_status = pi.input(NEW_TRIAL)
trial_number = 0

##function to catch the rising edge of a new trial signal
def check_trial():
        global trial_status
        global trial_number
        current_status = pi.input(NEW_TRIAL)
        if current_status != trial_status and current_status == True:
                trial_number +=1
        trial_status = current_status
                
                
# initialize the video stream and allow the camera
# sensor to warmup
print("[INFO] warming up cameras...")
vs1 = VideoStream(src=0, usePiCamera=False, resolution=(800,600),
                  framerate=args["fps"]).start()
vs2 = VideoStream(src=1, usePiCamera=False, resolution=(800,600),
                  framerate=args["fps"]).start()
time.sleep(2.0)

# initialize the FourCC, video writer, dimensions of the frame
fourcc = cv2.VideoWriter_fourcc(*args["codec"])
writer = None
(h, w) = (None, None)

animal_name = args["animal"]
session_name = args["session"]

##wait for start trigger
print("[INFO] waiting on start trigger...")
while not pi.input(SESSION_START):
        time.sleep(0.1)
print("[INFO] recording started!")

# loop over frames from the video stream
while pi.input(SESSION_START):
	# grab the frame from the video streams
	frame1 = vs1.read()
	frame2 = vs2.read()

	##check for a new trial
	check_trial()

	cv2.putText(frame1, animal_name, (5, 20),cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,0))
	cv2.putText(frame1, "Trial# "+str(trial_number), (200, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
	cv2.putText(frame1, session_name, (5, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,0))

	# check if the writer is None
	if writer is None:
		# store the image dimensions, initialzie the video writer,
		# and construct the zeros array
		(h, w) = frame1.shape[:2]
		writer = cv2.VideoWriter(args["output"], fourcc, args["fps"],
			(w*2, h), True)
		zeros = np.zeros((h, w), dtype="uint8")

	# construct the final output frame, storing the original frame
	# at the top-left, the red channel in the top-right, the green
	# channel in the bottom-right, and the blue channel in the
	# bottom-left
	output = np.zeros((h, w*2, 3), dtype="uint8")
	output[0:h, 0:w] = frame1
	output[0:h, w:w*2] = frame2

	# write the output frame to file
	writer.write(output)

	# show the frames
	cv2.imshow("Output", output)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
print("[INFO] Detected end of recording signal")
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs1.stop()
vs2.stop()
writer.release()
