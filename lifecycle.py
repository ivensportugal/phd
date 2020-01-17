from datetime import datetime
from constant import original_dir
from constant import preprocessed_dir
from file import identify_trajectories
import time

from relation import START
from relation import END
from relation import T_ENTER
from relation import T_LEAVE
from relation import C_IN
from relation import C_OUT
from relation import JOIN
from relation import DETACH
from relation import C_ENTER
from relation import C_LEAVE
from relation import GROUP
from relation import DISPERSE
from relation import MERGE
from relation import SPLIT


# Identify Lifecycles

def preprocess_size():

	clusters = identify_clusters(cluster_dir)

	for cluster in clusters:

		f_cluster      = open(cluster_dir       + cluster, 'r')
		f_preprocessed = open(preprocessed2_dir + cluster, 'w')

		cluster_size = 0

		for line in f_cluster:
			
			_timestamp  = datetime.strptime(line[0:19], '%Y-%m-%d %H:%M:%S')
			_event      = line[20:]

			cluster_event = parse_event(_event)
			cluster_size  = cluster_size + parse_size(cluster_event, _event)

			newline = _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + cluster_size + '\n'
			f_preprocessed.write(newline)

		f_cluster.close()
		f_preprocessed.close()



# Identifies the event the cluster went through

def parse_event(event_line):

	event_string = event_line[:event_line.index('(')]

	if event_string == 'start':    return START
	if event_string == 'end':      return END
	if event_string == 't_enter':  return T_ENTER
	if event_string == 't_leave':  return T_LEAVE
	if event_string == 'c_in':     return C_IN
	if event_string == 'c_out':    return C_OUT
	if event_string == 'join':     return JOIN
	if event_string == 'detach':   return DETACH
	if event_string == 'c_enter':  return C_ENTER
	if event_string == 'c_leave':  return C_LEAVE
	if event_string == 'group':    return GROUP
	if event_string == 'disperse': return DISPERSE
	if event_string == 'merge':    return MERGE
	if event_string == 'split':    return SPLIT

	return 0



# Identifies the size of the clsuter after the event

def parse_size(event_string, event_line):

	# all other events include squared brackets, thus their parsing can be summarized in one line of code
	if event_string == 't_enter' or event_string == 't_leave': return 1
	else: return event_line.count(',', event_line.index('['), event_line.index(']')) + 1

