##log_parse.py

##a set of functions to parse log files generated
##by behavior_box.py

##Ryan Neely
##July 2016

import numpy as np
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib import gridspec

"""
Takes in as an argument a log.txt files
Returns a dictionary of arrays containing the 
timestamps of individual events
"""
def parse_log(f_in):
	##open the file
	f = open(f_in, 'r')
	##set up the dictionary
	results = {
	"top_rewarded":[],
	"bottom_rewarded":[],
	"trial_start":[],
	"session_length":0,
	"reward_primed":[],
	"reward_idle":[],
	"top_lever":[],
	"bottom_lever":[],
	"rewarded_poke":[],
	"unrewarded_poke":[]
	}
	##run through each line in the log
	current_line = f.readline()
	while current_line != '':
		##figure out where the comma is that separates
		##the timestamp and the event label
		comma_idx = current_line.index(',')
		##the timestamp is everything in front of the comma
		timestamp = current_line[:comma_idx]
		##the label is everything after but not the return character
		label = current_line[comma_idx+1:-1]
		##now just put the timestamp in it's place!
		if label == "rewarded=top_lever":
			results['top_rewarded'].append(float(timestamp))
		elif label == "rewarded=bottom_lever":
			results['bottom_rewarded'].append(float(timestamp))
		elif label == "trial_begin":
			results['trial_start'].append(float(timestamp))
		elif label == "session_end":
			results['session_length'] = float(timestamp)
		elif label == "reward_primed":
			results['reward_primed'].append(float(timestamp))
		elif label == "reward_idle":
			results['reward_idle'].append(float(timestamp))
		elif label == "top_lever":
			results['top_lever'].append(float(timestamp))
		elif label == "bottom_lever":
			results['bottom_lever'].append(float(timestamp))
		elif label == "rewarded_poke":
			results['rewarded_poke'].append(float(timestamp))
		elif label == "unrewarded_poke":
			results['unrewarded_poke'].append(float(timestamp))
		else:
			print "unknown label: " + label
		##go to the next line
		current_line = f.readline()
	f.close()
	return results


def gauss_convolve(array, sigma):
	"""
	takes in an array with dimenstions samples x trials.
	Returns an array of the same size where each trial is convolved with
	a gaussian kernel with sigma = sigma.
	"""
	##remove singleton dimesions and make sure values are floats
	array = array.squeeze().astype(float)
	##allocate memory for result
	result = np.zeros(array.shape)
	##if the array is 2-D, handle each trial separately
	try:
		for trial in range(array.shape[1]):
			result[:,trial] = gaussian_filter(array[:, trial], sigma = sigma, order = 0, mode = "constant", cval = 0.0)
	##if it's 1-D:
	except IndexError:
		if array.shape[0] == array.size:
			result = gaussian_filter(array, sigma = sigma, order = 0, mode = "constant", cval = 0.0)
		else:
			print "Check your array dimenszions!"
	return result


"""
takes in a data dictionary produced by parse_log
plots the lever presses and the switch points for levers
"""
def plot_presses(data_dict, sigma = 90):
	##extract relevant data
	top = data_dict['top_lever']
	bottom = data_dict['bottom_lever']
	duration = np.ceil(data_dict['session_length'])
	top_rewarded = np.asarray(data_dict['top_rewarded'])/60.0
	bottom_rewarded = np.asarray(data_dict['bottom_rewarded'])/60.0
	##convert timestamps to histogram structures
	top, edges = np.histogram(top, bins = duration)
	bottom, edges = np.histogram(bottom, bins = duration)
	##smooth with a gaussian window
	top = gauss_convolve(top, sigma)
	bottom = gauss_convolve(bottom, sigma)
	##get plotting stuff
	x = np.linspace(0,np.ceil(duration/60.0), top.size)
	mx = max(top.max(), bottom.max())
	mn = min(top.min(), bottom.min())
	fig = plt.figure()
	gs = gridspec.GridSpec(2,2)
	ax = fig.add_subplot(gs[0,:])
	ax2 = fig.add_subplot(gs[1,0])
	ax3 = fig.add_subplot(gs[1,1], sharey=ax2)
	##the switch points
	ax.vlines(top_rewarded, mn, mx, colors = 'r', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "top rewarded")
	ax.vlines(bottom_rewarded, mn, mx, colors = 'b', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "bottom rewarded")
	ax2.vlines(top_rewarded, mn, mx, colors = 'r', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "top rewarded")
	ax2.vlines(bottom_rewarded, mn, mx, colors = 'b', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "bottom rewarded")
	ax3.vlines(top_rewarded, mn, mx, colors = 'r', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "top rewarded")
	ax3.vlines(bottom_rewarded, mn, mx, colors = 'b', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "bottom rewarded")
	ax.plot(x, top, color = 'r', linewidth = 2, label = "top lever")
	ax.plot(x, bottom, color = 'b', linewidth = 2, label = "bottom_lever")
	ax.legend()
	ax.set_ylabel("press rate", fontsize = 14)
	fig.suptitle("Lever press performance", fontsize = 18)
	ax.set_xlim(-1, x[-1]+1)
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	#plot them separately
	##figure out the order of lever setting to create color spans
	# if top_rewarded.min() < bottom_rewarded.min():
	# 	for i in range(top_rewarded.size):
	# 		try:
	# 			ax2.axvspan(top_rewarded[i], bottom_rewarded[i], facecolor = 'r', alpha = 0.2)
	# 		except IndexError:
	# 			ax2.axvspan(top_rewarded[i], duration, facecolor = 'r', alpha = 0.2)
	# else:
	# 	for i in range(bottom_rewarded.size):
	# 		try:
	# 			ax3.axvspan(bottom_rewarded[i], top_rewarded[i], facecolor = 'b', alpha = 0.2)
	# 		except IndexError:
	# 			ax3.axvspan(bottom_rewarded[i], duration, facecolor = 'b', alpha = 0.2)
	ax2.plot(x, top, color = 'r', linewidth = 2, label = "top lever")
	ax3.plot(x, bottom, color = 'b', linewidth = 2, label = "bottom_lever")
	ax2.set_ylabel("press rate", fontsize = 14)
	ax2.set_xlabel("Time in session, mins", fontsize = 14)
	ax3.set_xlabel("Time in session, mins", fontsize = 14)
	fig.suptitle("Lever press performance", fontsize = 18)
	ax2.set_xlim(-1, x[-1]+1)
	ax3.set_xlim(-1, x[-1]+1)
	for tick in ax2.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in ax2.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in ax3.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in ax3.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	ax2.set_title("top only", fontsize = 14)
	ax3.set_title("bottom only", fontsize = 14)








