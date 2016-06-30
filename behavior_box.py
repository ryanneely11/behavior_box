"""
behavior_box.py

ryan neely

A script to control the raspberry pi that is used
to interface with the behavior box.

GUI application adapted from GitHub user scotty3785
"""

"""
TODO:
-create a separate script that will run the actual task.
	integrate a button to start/stop the task a la BMI_GUI

-Add text boxes that count the number of presses/nose port entries etc.

-Add GUI variables to control reward values, intervals, etc

-Add a button to reset counts
""" 

import sys

if(sys.version_info[0]<3):
	from Tkinter import *
else:
	from tkinter import *
	
import RPi.GPIO as pi
import math

##define port numbers
inputs = {
"nose_poke":26,
"lever_1":17,
"lever_2":27
}

outputs = {
"h20":13,
"led":20,
"C1":12, #C1 = bitmask 2 (on TDT)
"C3":23, #C3 = bitmask 8
"C5":24, #C5 = bitmask 32
"C7":25 #C7 = bitmask 128
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
			self.state = state
			self.updateLED()	

	def outputOn(self):
		"""If the pin is an output pin, turn the output on, check the box, 
		and change the LED"""
		if self.isOutput():
			self.set_state.select()
			self.set_state.invoke()

	def outputOff(self):
		"""If the pin is an output pin, turn the output off, uncheck the box, 
		and change the LED"""
		if self.isOutput():
			self.set_state.deselect()
			self.set_state.invoke()


class App(Frame):
	def __init__(self,parent=None, **kw):
		Frame.__init__(self,parent,**kw)
		self.parent = parent
		self.ports = []
		## Get the RPI Hardware dependant list of GPIO
		#gpio = self.getRPIVersionGPIO()
		for n, key in enumerate(inputs.keys()):
			self.ports.append(GPIO(self,pin=inputs[key],name=key))
			self.ports[-1].grid(row=n, column=0)
		for n, key in enumerate(outputs.keys()):
			self.ports.append(GPIO(self,pin=outputs[key],name=key))
			self.ports[-1].grid(row=n,column=1)
		self.update()

	def onClose(self):
		"""This is used to run the Rpi.GPIO cleanup() method to return pins to be an input
		and then destory the app and its parent."""
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
			port.updateOutput()
					
	def update(self):
		"""Runs every 20ms to update the state of the GPIO inputs"""
		self.readStates()
		self._timer = self.after(20,self.update)
		

def main():
	root = Tk()
	root.title("Raspberry Pi GPIO")
	a = App(root)
	a.grid()
	"""When the window is closed, run the onClose function."""
	root.protocol("WM_DELETE_WINDOW",a.onClose)
	root.resizable(False,False)
	root.mainloop()
   

if __name__ == '__main__':
	main()