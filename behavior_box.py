"""
behavior_box.py

ryan neely

A script to control the raspberry pi that is used
to interface with the behavior box.

"""

"""
TODO:

-logging function records events continuously while
	they happen

""" 

import sys

if(sys.version_info[0]<3):
	from Tkinter import *
else:
	from tkinter import *
	
import RPi.GPIO as pi
import math
import time
import numpy as np

##file path to save data
FILEPATH = "/home/pi/Desktop/test.txt"

##define port numbers
inputs = {
"nose_poke":26,
"top_lever":17,
"bottom_lever":27
}

outputs = {
"h20":13,
"led":20,
"C1":12, #C1 = bitmask 2 (on TDT)
"C3":23, #C3 = bitmask 8
"C5":24, #C5 = bitmask 32
"C7":25, #C7 = bitmask 128

"buzz_1":6, ##push pin for buzzer
"buzz_2":5  ##pull pin for buzzer
}

##set up the GPIO board to the appropriate settings
pi.setmode(pi.BCM) #to use the BCM pin mapping

##set input pins
for key in inputs.keys():
	pi.setup(inputs[key], pi.IN)

for key in outputs.keys():
	pi.setup(outputs[key], pi.OUT)

##set the pull up resistor for the levers
pi.setup([17,27],pi.IN, pull_up_down = pi.PUD_DOWN)


"""some functions to deliver outputs"""

def buzzer(samples = 75):
	"""a function to generate a brief buzzer tone"""
	for i in range(samples):
		pi.output(outputs["buzz_1"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_1"], False)
		pi.output(outputs["buzz_2"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_2"], False)
	return 0

def buzzer2(samples = 75):
	"""a function to generate a brief buzzer tone"""
	for i in range(samples):
		pi.output(outputs["buzz_1"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_1"], False)
		pi.output(outputs["buzz_2"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_2"], False)
	time.sleep(0.1)
	for i in range(samples):
		pi.output(outputs["buzz_1"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_1"], False)
		pi.output(outputs["buzz_2"], True)
		time.sleep(.001)
		pi.output(outputs["buzz_2"], False)
	return 0

def h20reward(duration):
	pi.output(outputs['h20'], True)
	time.sleep(duration)
	pi.output(outputs['h20'], False)

def lightswitch(state):
	if state == "on":
		pi.output(outputs['led'], True)
	elif state == "off":
		pi.output(outputs['led'], False)


###gui stuff###

class LED(Frame):
	"""A Tkinter LED Widget.
	a = LED(root,10)
	a.set(True)
	current_state = a.get()"""
	OFF_STATE = 0
	ON_STATE = 1
	
	def __init__(self,master,size=10,**kw):
		self.size = size
		Frame.__init__(self,master,width=size,height=size)
		self.configure(**kw)
		self.state = LED.OFF_STATE
		self.c = Canvas(self,width=self['width'],height=self['height'])
		self.c.grid()
		self.led = self._drawcircle((self.size/2)+1,(self.size/2)+1,(self.size-1)/2)
	def _drawcircle(self,x,y,rad):
		"""Draws the circle initially"""
		color="red"
		return self.c.create_oval(x-rad,y-rad,x+rad,y+rad,width=rad/5,fill=color,outline='black')
	def _change_color(self):
		"""Updates the LED colour"""
		if self.state == LED.ON_STATE:
			color="green"
		else:
			color="red"
		self.c.itemconfig(self.led, fill=color)
	def set(self,state):
		"""Set the state of the LED to be True or False"""
		self.state = state
		self._change_color()
	def get(self):
		"""Returns the current state of the LED"""
		return self.state

class GPIO(Frame):
	"""Each GPIO class draws a Tkinter frame containing:
	- A Label to show the GPIO Port Name
	- A data direction spin box to select pin as input or output
	- A checkbox to set an output pin on or off
	- An LED widget to show the pin's current state
	- A Label to indicate the GPIOs current function"""
	
	def __init__(self,parent,pin=0,name=None,**kw):
		self.pin = pin
		if name == None:
			self.name = "GPIO %02d" % (self.pin)
		else:
			self.name = name
		Frame.__init__(self,parent,width=150,height=20,relief=SUNKEN,bd=1,padx=5,pady=5)
		##Future capability
		##self.bind('<Double-Button-1>', lambda e, s=self: self._configurePin(e.y))
		self.parent = parent
		self.configure(**kw)
		self.state = False
		self.cmdState = IntVar()
		self.Label = Label(self,text=self.name)
		self.current_mode = StringVar()
		self.current_mode.set(self.getPinFunctionName())
		self.mode_sel = Label(self,textvariable=self.current_mode)
		self.set_state = Checkbutton(self,text="High/Low",variable=self.cmdState,command=self.toggleCmdState)
		self.led = LED(self,20)
		self.Label.grid(column=0,row=0)
		self.mode_sel.grid(column=1,row=0)
		self.set_state.grid(column=2,row=0)

		self.led.grid(column=3,row=0)

		self.set_state.config(state=DISABLED)

		##the total counts
		self.count = 0
		self.countVar = StringVar()
		self.countVar.set(str(self.count))
		self.countLabel = Label(self, textvariable = self.countVar)
		self.countLabel.grid(column=4,row=0)

		if (self.current_mode.get() == "Input"):
			self.set_state.config(state=DISABLED)
		elif (self.current_mode.get() == "Output"):
			self.set_state.config(state=NORMAL)
		else:
			self.set_state.config(state=DISABLED)
			pi.cleanup(self.pin)
		self.updateInput()

	def isInput(self):
		"""Returns True if the current pin is an input"""
		return (self.current_mode.get() == "Input")

	def isOutput(self):
		"""Returns True if the current pin is an output"""
		return (self.current_mode.get() == "Output")

	def getPinFunctionName(self):
		pin = self.pin
		functions = {1:'Input',
					 0:'Output',
					 42:'I2C',
					 41:'SPI',
					 43:'HARD_PWM',
					 40:'Serial',
					 -1:'Unknown'}                     
		return functions[pi.gpio_function(pin)]

	def toggleCmdState(self):
		"""Reads the current state of the checkbox, updates LED widget
		and sets the gpio port state."""
		self.state = self.cmdState.get()
		self.updateLED()
		self.updatePin()
		##only update count if the output is being turned on
		if self.state == True:
			self.incrementCount()

	def updatePin(self):
		"""Sets the GPIO port state to the current state"""
		pi.output(self.pin,self.state)

	def updateLED(self):
		"""Refreshes the LED widget depending on the current state"""
		self.led.set(self.state)

	def updateInput(self):
		"""Updates the current state if the pin is an input and sets the LED"""
		if self.isInput():
			state = pi.input(self.pin)
			new_input = False
			if state != self.state and state == True:
				new_input = True
			self.state = state
			self.updateLED()
			if new_input:
				self.incrementCount()	

	def outputOn(self):
		"""If the pin is an output pin, turn the output on, check the box, 
		and change the LED"""
		if self.isOutput():
			self.set_state.select()
			self.set_state.invoke()
			self.incrementCount()

	def outputOff(self):
		"""If the pin is an output pin, turn the output off, uncheck the box, 
		and change the LED"""
		if self.isOutput():
			self.set_state.deselect()
			self.set_state.invoke()

	def incrementCount(self):
		"""a function to update the count of events"""
		self.count +=1
		self.countVar.set(str(self.count))

	def resetCount(self):
		"""a function to reset the counter"""
		self.count = 0
		self.countVar.set(str(self.count))

	def getState(self):
		"""returns on or off state; useful for checking
			the state of an output port"""
		return pi.input(self.pin)



class entryBox(object):
	"""Tkinter object that contains some editable text"""
	def __init__(self, homeFrame, labelText, preset, grid_row, grid_col):
		self.homeFrame = homeFrame
		self.labelText = labelText
		self.preset = preset
		self.entryString = StringVar()
		self.entryObj = Entry(homeFrame, textvariable = self.entryString)
		self.title = Label(self.homeFrame, text = self.labelText)
		self.entryString.set(self.preset)
		self.title.grid(row = grid_row, column = grid_col)
		self.entryObj.grid(row = grid_row+1, column = grid_col)

class App(Frame):
	def __init__(self,parent=None, **kw):
		Frame.__init__(self,parent,**kw)
		self.parent = parent
		"""state variables"""
		self.ports = []
		self.startTime = None ##timestamp that training starts; all times relative to this
		self.active = IntVar() ##is the program running?
		self.trial_running = False ##has a trial been signaled?
		self.primed = False ##is the reward port primed?
		self.rewarded = None
		self.unrewarded = None
		self.waiting = False
		self.trialEnded = None
		self.newTrialStart = None
		self.fileout = open(FILEPATH, 'w')##file to save the timestamps
		## Get the RPI Hardware dependant list of GPIO
		#gpio = self.getRPIVersionGPIO()
		for n, key in enumerate(inputs.keys()):
			self.ports.append(GPIO(self,pin=inputs[key],name=key))
			self.ports[-1].grid(row=n, column=0)
		for n, key in enumerate(outputs.keys()):
			self.ports.append(GPIO(self,pin=outputs[key],name=key))
			self.ports[-1].grid(row=n,column=1)
		

		###entry boxes for setting reward parameters
		self.reward_time_entry = entryBox(self, "Reward time", "1.0", 3,2)
		self.reward_rate_entry = entryBox(self, "Reward chance", "0.75",5,2)
		self.ITI_entry = entryBox(self, "inter-trial-interval", "6",7,2)

		#other objects for setting task params
		self.selectLever = Spinbox(self, values = ("top_lever", "bottom_lever"), wrap = False, command = self.setLevers)
		self.selectLever.grid(row = 0, column = 2)
		self.setActive = Checkbutton(self,text="Activate box",variable=self.active, command = self.activate)
		self.setActive.grid(row = 1, column = 2)
		self.resetCounts = Button(self, text = "Reset Counts", command = self.counterReset)
		self.resetCounts.grid(row = 2, column = 2)

		self.update()

	def setLevers(self):
		"""a function to set the rewarded and unrewarded levers"""
		if self.selectLever.get() == "top_lever":
			self.rewarded = "top_lever"
			self.unrewarded = "bottom_lever"
		elif self.selectLever.get() == "bottom_lever":
			self.rewarded = "bottom_lever"
			self.unrewarded = "top_lever"
		self.logAction(time.time(), "rewarded="+self.selectLever.get())

	def counterReset(self):
		"""function to reset the displayed counters"""
		for port in self.ports:
			port.resetCount()

	def activate(self):
		"""function to set the start time clock"""
		##set the start time
		self.startTime = time.time()
		self.newTrialStart = self.startTime+(abs(np.random.randn())*float(self.ITI_entry.entryString.get()))
		self.waiting = True
		self.setLevers()
		self.counterReset()

	def logAction(self, timestamp, label):
		"""function to log the timestamp of a particular action"""
		self.fileout.write(str(timestamp-self.startTime)+","+label)
		self.fileout.write("\n")

	def initTrial(self):
		"""function to start a new trial"""
		self.logAction(time.time(), "trial_begin")
		self.trial_running = True
		lightswitch("on")
		buzzer2()
		self.waiting = False

	def endTrial(self, port_name):
		"""function to end a trial"""
		self.trial_running = False
		lightswitch("off")
		buzzer()
		if port_name == self.rewarded:
			if np.random.random() <= float(self.reward_rate_entry.entryString.get()):
				self.primed = True
				self.logAction(time.time(),"reward_primed")
		else:
			self.logAction(time.time(),"reward_idle")

	def resetTrial(self):
		"""a function to reset the trial"""
		self.trialEnded = time.time()
		self.newTrialStart = self.trialEnded+(abs(np.random.randn())*float(self.ITI_entry.entryString.get()))
		self.waiting = True

	def checkTimer(self):
		if self.waiting == True:
			if time.time() >= self.newTrialStart:
				self.initTrial()


	def onClose(self):
		"""This is used to run the Rpi.GPIO cleanup() method to return pins to be an input
		and then destory the app and its parent."""
		self.fileout.close()
		try:
			pi.cleanup()
		except RuntimeWarning as e:
			print(e)
		self.destroy()
		self.parent.destroy()

	def readStates(self):
		"""Cycles through the assigned ports and updates them based on the GPIO input"""
		for port in self.ports:
			port.updateInput()
			##check to see if the box is active
			if self.active.get():
				##check timing stuff
				self.checkTimer()
				"""check for active inputs and log them"""
				##top lever
				if port.name == "top_lever" and port.state ==True:
					self.logAction(time.time(), "top_lever")
					if self.trial_running:
						self.endTrial(port.name)
				##bottom lever
				if port.name == "bottom_lever" and port.state == True:
					self.logAction(time.time(), "bottom_lever")
					if self.trial_running:
						self.endTrial(port.name)
				##nose poke 
				if port.name == "nose_poke" and port.state == True:
					self.logAction(time.time(), "nose_poke")
					if self.trial_running == False and self.primed == True:
						h20reward(float(self.reward_time_entry.entryString.get()))
						self.logAction(time.time(), "reward_delivered")
						self.primed = False
						self.resetTrial()
					elif self.trial_running == False:
						self.logAction(time.time(), "unrewarded_entry")
						self.resetTrial()

					
	def update(self):
		"""Runs every 20ms to update the state of the GPIO inputs"""
		self.readStates()
		self._timer = self.after(20,self.update)

def main():
	root = Tk()
	root.title("Rat box")
	a = App(root)
	a.grid()
	"""When the window is closed, run the onClose function."""
	root.protocol("WM_DELETE_WINDOW",a.onClose)
	root.resizable(False,False)
	root.mainloop()
   

if __name__ == '__main__':
	main()
