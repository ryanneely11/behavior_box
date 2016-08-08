##a script to record video of animals in the behavior box

import cv2
import multiprocessing as mp
import RPi.GPIO as pi
import time

##GPIO setup
pi.setmode(pi.BCM)
##setup GPIO ports
inputs = {
	"session_running":18,
	"trial_running":19
}

for key in inputs:
	pi.setup(inputs['key'], pi.IN)

## default file to store data
save_folder = "/home/pi/Desktop/video/Day0.avi"
##initialize a video capture object
cap = cv2.VideoCapture(0)
##specify the video codec
fourcc = cv2.VideoWriter_fourcc(*'XVID')

def capture(file_path = None, animal_name = "AnimalX", session = "Day0"):
	if file_path = None:
		file_path = save_folder
	##create a videoWriter object
	writer = cv2.VideoWriter(file_path)
	##a counter to count the trials
	trial_number = 0
	##wait for the session to begin (triggered by behavior box)
	while not pi.input(inputs['session_running']):
		time.sleep(0.2)
	##when the session begins, run this loop until it ends
	while pi.input(inputs['session_running']):
		##check to see if a trial has started
		while pi.input(inputs['trial_running']):
			##get the video frame
			ret, frame = cap.read()
			##add some text in the corner about the trial and animal
			cv2.putText(frame, "Trial "+str(trial_number), (5, 20),
				cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
			cv2.putText(frame, animal_name, (200, 20), 
				cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
			cv2.putText(frame, session, (5, 40), 
				cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
			##write the video frame to file
			writer.write(frame)
			cv2.imshow('frame', frame)
	cap.release()
	out.release()
	cv2.destroyAllWindows()



