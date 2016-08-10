# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output video file")
ap.add_argument("-f", "--fps", type=int, default=32,
	help="FPS of output video")
ap.add_argument("-c", "--codec", type=str, default="MJPG",
	help="codec of output video")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera
# sensor to warmup
print("[INFO] warming up cameras...")
vs1 = VideoStream(src=0, usePiCamera=False, resolution=(1080,720)).start()
vs2 = VideoStream(src=1, usePiCamera=False, resolution=(1080,720)).start()
time.sleep(2.0)

# initialize the FourCC, video writer, dimensions of the frame
fourcc = cv2.VideoWriter_fourcc(*args["codec"])
writer = None
(h, w) = (None, None)

# loop over frames from the video stream
while True:
	# grab the frame from the video streams
	frame1 = vs.read()
	frame2 = vs.read()

	cv2.putText(frame1, "Animal_name", (5, 20),cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
	cv2.putText(frame1, "Session_number", (200, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
	cv2.putText(frame1, "Trial_number", (5, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))

	# check if the writer is None
	if writer is None:
		# store the image dimensions, initialzie the video writer,
		# and construct the zeros array
		(h, w) = frame.shape[:2]
		writer = cv2.VideoWriter(args["output"], fourcc, args["fps"],
			(w, h*2), True)
		zeros = np.zeros((h, w), dtype="uint8")

	# construct the final output frame, storing the original frame
	# at the top-left, the red channel in the top-right, the green
	# channel in the bottom-right, and the blue channel in the
	# bottom-left
	output = np.zeros((h * 2, w * 2, 3), dtype="uint8")
	output[0:h, 0:w] = frame1
	output[h:h * 2, 0:w] = frame2

	# write the output frame to file
	writer.write(output)

	# show the frames
	cv2.imshow("Output", output)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
writer.release()