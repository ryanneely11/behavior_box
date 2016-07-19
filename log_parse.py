##log_parse.py

##a set of functions to parse log files generated
##by behavior_box.py

##Ryan Neely
##July 2016

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