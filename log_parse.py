##log_parse.py

##a set of functions to parse log files generated
##by behavior_box.py

##Ryan Neely
##July 2016

import numpy as np
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib import gridspec
import time
import os
import glob
import h5py

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
	label, timestamp = read_line(f.readline())
	while  label is not None:
		##now just put the timestamp in it's place!
		if label == "rewarded=top_lever":
			results['top_rewarded'].append(float(timestamp))
		elif label == "rewarded=bottom_lever":
			results['bottom_rewarded'].append(float(timestamp))
		elif label == "trial_begin":
			results['trial_start'].append(float(timestamp))
		elif label == "session_end":
			results['session_length'] = [float(timestamp)]
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
		label, timestamp = read_line(f.readline())
	f.close()
	return results

##a sub-function to parse a single line in a log, 
##and return the timestamp and label components seperately
def read_line(string):
	label = None
	timestamp = None
	if string is not '':
		##figure out where the comma is that separates
		##the timestamp and the event label
		comma_idx = string.index(',')
		##the timestamp is everything in front of the comma
		timestamp = string[:comma_idx]
		##the label is everything after but not the return character
		label = string[comma_idx+1:-1]
	return label, timestamp


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
	duration = int(np.ceil(data_dict['session_length']))
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

##similar to above, but instead of raw press rates, we are plotting
##the percent of choice for each press type
def plot_percent_choice(data_dict, sigma = 50):
	##extract relevant data
	top = data_dict['top_lever']
	bottom = data_dict['bottom_lever']
	duration = int(np.ceil(data_dict['session_length']))
	top_rewarded = np.asarray(data_dict['top_rewarded'])/60.0
	bottom_rewarded = np.asarray(data_dict['bottom_rewarded'])/60.0
	##convert timestamps to histogram structures
	top, edges = np.histogram(top, bins = duration)
	bottom, edges = np.histogram(bottom, bins = duration)
	##smooth with a gaussian window
	top = gauss_convolve(top, sigma)
	bottom = gauss_convolve(bottom, sigma)
	##get the percentages
	top = top/(top+bottom)
	bottom = bottom/(top+bottom)
	##get plotting stuff
	x = np.linspace(0,np.ceil(duration/60.0), top.size)
	mx = 1.1
	mn = -.1
	fig = plt.figure()
	ax = fig.add_subplot(111)
	##the switch points
	ax.vlines(top_rewarded, mn, mx, colors = 'r', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "top rewarded")
	ax.vlines(bottom_rewarded, mn, mx, colors = 'b', linestyles = 'dashed', 
		linewidth = '2', alpha = 0.5, label = "bottom rewarded")
	ax.plot(x, top, color = 'r', linewidth = 2, label = "top lever")
	ax.plot(x, bottom, color = 'b', linewidth = 2, label = "bottom_lever")
	ax.legend()
	ax.set_ylabel("percent of choices", fontsize = 14)
	ax.set_xlabel("Time in session (min)", fontsize = 14)
	fig.suptitle("Lever press performance", fontsize = 18)
	ax.set_xlim(-1, x[-1]+1)
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)


##a function to extract the creation date (expressed as the 
##julian date) in integer format of a given filepath
def get_cdate(path):
	return int(time.strftime("%j", time.localtime(os.path.getctime(path))))


##takes in a dictionary returned by parse_log and returns the 
##percent correct. Chance is the rewarded chance rate for the active lever.
##function assumes the best possible performance is the chance rate.
def get_p_correct(result_dict, chance = 0.9):
	total_trials = len(result_dict['top_lever'])+len(result_dict['bottom_lever'])
	correct_trials = len(result_dict['rewarded_poke'])
	return (float(correct_trials)/total_trials)/chance

##takes in a dictionary returned by parse_log and returns the 
##success rate (mean for the whole session)
def get_success_rate(result_dict):
	correct_trials = len(result_dict['rewarded_poke'])
	session_len = result_dict['session_length']/60.0
	return float(correct_trials)/session_len

##returns a list of file paths for all log files in a directory
def get_log_file_names(directory):
	##get the current dir so you can return to it
	cd = os.getcwd()
	filepaths = []
	os.chdir(directory)
	for f in glob.glob("*.txt"):
		filepaths.append(os.path.join(directory,f))
	os.chdir(cd)
	return filepaths

def plot_epoch(directory, plot = True):
	##grab a list of all the logs in the given directory
	fnames = get_log_file_names(directory)
	##x-values are the julian date of the session
	dates = [get_cdate(f) for f in fnames]
	##y-values are the success rates (or percent correct?) for each session
	scores = []
	for session in fnames:
		# print "working on session "+ session
		result = parse_log(session)
		# print "score is "+str(get_success_rate(result))
		scores.append(get_success_rate(result))
	##convert lists to arrays for the next steps
	dates = np.asarray(dates)
	scores = np.asarray(scores)
	##files may not have been opened in order of ascending date, so sort them
	sorted_idx = np.argsort(dates)
	dates = dates[sorted_idx]
	##adjust dates so they start at 0
	dates = dates-(dates[0]-1)
	scores = scores[sorted_idx]
	##we want to not draw lines when there are non-consecutive training days:
	##our x-axis will then be a contiuous range of days
	x = range(1,dates[-1]+1)
	##insert None values in the score list when a date was skipped
	skipped = []
	for idx, date in enumerate(x):
		if date not in dates:
			scores = np.insert(scores,idx,np.nan)
	if plot:
		fig = plt.figure()
		ax = fig.add_subplot(1,1,1)
		ax.plot(x, scores, 'o', color = "c")
		ax.set_xlabel("Training day")
		ax.set_ylabel("Correct trials per min")
	return x, dates, scores

def plot_epochs_multi(directories):
	
	##assume the folder name is the animal name, and that is is two chars
	fig = plt.figure()
	ax = fig.add_subplot(111)
	for d in directories:
		name = d[-2:]
		x, dates, scores = plot_epoch(d, plot = False)
		##get a random color to plot this data with
		c = np.random.rand(3,)
		ax.plot(x, scores, 's', markersize = 10, color = c)
		ax.plot(x, scores, linewidth = 2, color = c, label = name)
	ax.legend(loc=2)
	##add horizontal lines showing surgery and recording days
	x_surg = [16,17,18,19]
	y_surg = [-.1,-.1,-.1,-.1]
	x_rec = range(25,44)
	y_rec = np.ones(len(x_rec))*-0.1
	x_pre = range(0,15)
	y_pre = np.ones(len(x_pre))*-0.1
	ax.plot(x_surg, y_surg, linewidth = 4, color = 'k')
	ax.plot(x_pre, y_pre, linewidth = 4, color = 'c')
	ax.plot(x_rec, y_rec, linewidth =4, color = 'r')
	ax.text(15,-0.32, "Surgeries", fontsize = 12)
	ax.text(32,-0.32, "Recording", fontsize = 12)
	ax.text(4,-0.32, "Pre-trainig", fontsize = 12)		
	ax.set_xlabel("Training day", fontsize=16)
	ax.set_ylabel("Correct trials per min", fontsize=16)
	fig.suptitle("Performance across days", fontsize=16)

##takes in a dictionary created by the log_parse function and 
##saves it as an hdf5 file
def dict_to_h5(d, path):
	f_out = h5py.File(path, 'w-')
	##make each list into an array, then a dataset
	for key in d.keys():
		##create a dataset with the same name that contains the data
		f_out.create_dataset(key, data = np.asarray(d[key]))
	##and... that's it.
	f_out.close()

##converts all the txt logs in a given directory to hdf5 files
def batch_log_to_h5(directory):
	log_files = get_log_file_names(directory)
	for log in log_files:
		##generate the dictionary
		result = parse_log(log)
		##save it as an hdf5 file with the same name
		new_path = os.path.splitext(log)[0]+'.hdf5'
		dict_to_h5(result, new_path)
	print 'Save complete!'

##offsets all timestamps in a log by a given value
##in a h5 file like the one produced by the above function
def offset_log_ts(h5_file, offset):
	f = h5py.File(h5_file, 'r+')
	for key in f.keys():
		new_data = np.asarray(f[key])+offset
		f[key][:] = new_data
	f.close()



##a function that generates a 3-D array, where one column is actions
##one is outcome and the other is the timestamp. This is a different way of parsing
##the log files. 
def generate_ao_list(f_in):
	##open the file
	f = open(f_in, 'r')
	##set up the results list
	actions = []
	outcomes = []


##a sub-function to get all the events that take place within each trial in a session
def get_trial_sets(f_in):
	##open the file
	f = open(f_in, 'r')
	##set up a list to store the trial lists
	trials = []
	label, timestamp = read_line(f.readline())
	while label is not None:
		##look for the start of a new trial
		if label == "trial_begin":
			##create a new trial list
			trial = []
			trial.append([label, timestamp])
			label, timestamp = read_line(f.readline())
			while label != None and label != "trial_begin":
				trial.append([label, timestamp])
				label, timestamp = read_line(f.readline())
			trials.append(trial)
		label, timestamp = read_line(f.readline())
	f.close()
	return trials

