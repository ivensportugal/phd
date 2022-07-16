from datetime import datetime
from datetime import timedelta

from constant import original_dir
from constant import preprocessed_dir
from constant import rate
from constant import wait_constant
from constant import min_cluster
from file import identify_trajectories

from cluster import dbscan

from relation import calc_relations
from relation import calc_cluster_id
from relation import save_relations

import numpy as np
from numpy.lib.recfunctions import append_fields

import time
import ciso8601

from validation import validate






## Process trajectories.
## Identify clusters, store their lifecycle

def process():

	trajectories = identify_trajectories(preprocessed_dir)
	# f_preprocessed = []
	# for trajectory in trajectories:
	# 	f_preprocessed.append(open(preprocessed_dir + trajectory, 'r'))

	f_preprocessed = [open(preprocessed_dir + trajectory, 'r') for trajectory in  trajectories]

	datapoints = [format_datapoint(trajectory.readline().split(',')) for trajectory in f_preprocessed] # starting datapoints, assumes files contain data, [[int, time, float, float]]
	timestamps = [datapoint[1] for datapoint in datapoints] # the first timestamp of every file, assumes files contain data

	timeline = min(timestamps) # The universal timeline
	timeline_rate = timedelta(minutes=rate)


	#clusters_curr_timestamp = np.array([], dtype=[('tid','i4'),('lat','f4'),('lon','f4'),('cid','i4')]) # 'tid', 'lat', 'lon', 'cid' <- these are labels - int, float, float, int
	#clusters_prev_timestamp = np.array([], dtype=[('tid','i4'),('lat','f4'),('lon','f4'),('cid','i4')]) # 'tid', 'lat', 'lon', 'cid' <- these are labels - int, float, float, int

	clusters_curr_timestamp = np.array([]) # int, float, float, int
	clusters_prev_timestamp = np.array([]) # int, float, float, int

	while(True):

		datapoints = [calculate_next_datapoint(trajectory, timeline, timeline_rate, datapoints[i]) for i, trajectory in enumerate(f_preprocessed)]
		timestamps = [datapoint[1] if datapoint != None else None for datapoint in datapoints]


		# Stop Condition: If all files have been read, stop
		if all(datapoint == None for datapoint in datapoints): break

		# Performs DBSCAN only on those points that are valid (less than universal timestamp)
		#datapoints_valid = np.array([(datapoints[i][0], datapoints[i][2], datapoints[i][3]) for i, timestamp in enumerate(timestamps) if timestamp != None and timeline >= timestamp], dtype=[('tid','i4'),('lat','f4'),('lon','f4')])
		#datapoints_valid_temp = datapoints_valid[list(datapoints_valid.dtype.names[1:])].copy() # get lats and longs
		#db = dbscan(datapoints_valid_temp.view(np.float32).reshape(datapoints_valid_temp.shape + (-1,))).labels_ # performs dbscan and get labels
		#clusters_curr_timestamp = append_fields(datapoints_valid, 'cid', data = tuple(db), dtypes='i4', usemask=False)
		#clusters_curr_timestamp['cid'] = (clusters_curr_timestamp['cid']*-1-1)  # so traj without clusters have cluster id zero, internal are negative, external are positive


		# print timeline


		datapoints_valid = np.array([(datapoints[i][0], datapoints[i][2], datapoints[i][3]) for i, timestamp in enumerate(timestamps) if timestamp != None and timeline >= timestamp and timeline - timestamp <= wait_constant*timeline_rate])

		# if datapoints_valid == []:
		# 	timeline_line = str(timeline) + ',0,0' # time + num_traj + num_clusters
		# 	# print timeline_line


		clusters_curr_timestamp = []
		if datapoints_valid != []:
			clusters_curr_timestamp = datapoints_valid[:,1:].copy() # get lats and longs
			labels = dbscan(clusters_curr_timestamp) # performs dbscan and get labels

			

			# uniqui = np.unique(labels)
			# aclusters = uniqui[uniqui >= 0]
			# timeline_line = str(timeline) + ',' + str(len(datapoints_valid)) + ',' + str(len(aclusters))
			# # print timeline_line




################# Validation Tasks #############################
################################################################
			# validate(clusters_curr_timestamp, labels)
################################################################
################################################################



			clusters_curr_timestamp = np.zeros((datapoints_valid.shape[0],datapoints_valid.shape[1]+1)) # adds a column
			clusters_curr_timestamp[:,:-1] = datapoints_valid
			clusters_curr_timestamp[:,-1:] = np.array([labels]).transpose()  # add labels as the last column
			clusters_curr_timestamp[:,-1:] = clusters_curr_timestamp[:,-1:]*-1-1  # so traj without clusters have cluster id zero, internal are negative, external are positive


		# Calculate Relations
		dict_clusters_prev_timestamp, dict_clusters_curr_timestamp = calc_relations(clusters_prev_timestamp, clusters_curr_timestamp)
		

		# Assign universal cluster ids and update cluster ids
		calc_cluster_id(clusters_prev_timestamp, clusters_curr_timestamp, dict_clusters_prev_timestamp, dict_clusters_curr_timestamp)

		# Assign coordinates
		calc_cluster_coordinates(clusters_prev_timestamp, clusters_curr_timestamp, dict_clusters_prev_timestamp, dict_clusters_curr_timestamp)

		# Save Relations
		save_relations(dict_clusters_prev_timestamp, dict_clusters_curr_timestamp, timeline-timeline_rate, timeline)
		


		# Updates for next iteration: cluster list and timeline
		clusters_prev_timestamp = np.copy(clusters_curr_timestamp)
		timeline = update_timeline(timeline, timeline_rate, timestamps, clusters_prev_timestamp, f_preprocessed)


	for file in f_preprocessed:
		file.close()




# A helper function in process()
# Given a trajectory (file), find the timestamp (line) just before the universal timeline
# A trajectory and a datapoint have to be passed because, in some cases, the algorithm needs to give one step back
def calculate_next_datapoint(traj, tl, tl_rate, prev_datapoint):

	# Already reached EOF
	if prev_datapoint is None: return None

	# Checks if needs to update
	if prev_datapoint[1] >= tl:
		return prev_datapoint

	# Tries to update
	pos = traj.tell()
	curr_datapoint = prev_datapoint

	# Timeline is always set, use it
	while True:
		line = traj.readline()
		if line == '': break # EOF
		if ciso8601.parse_datetime(line.split(',')[1]) > tl:
			traj.seek(pos)
			break #return curr_datapoint
		pos = traj.tell()
		curr_datapoint = format_datapoint(line.split(','))

	# If the timestamp I have is old, then do not use it. It has been processed already
	if (tl - curr_datapoint[1]) >= wait_constant*tl_rate:
		line = traj.readline()
		if line == '': return None
		if line == None: return None
		curr_datapoint = format_datapoint(line.split(','))
		return curr_datapoint
	else:
		return curr_datapoint


# A function to skip timestamps where nothing happens
def update_timeline(timeline, timeline_rate, timestamps, clusters_prev_timestamp, f_preprocessed):

	if (len(clusters_prev_timestamp) >= min_cluster): return timeline + timeline_rate

	# save the current timestamps
	possible_timelines = [ts for ts in timestamps if ts != None and ts > timeline]

	# perform one iteration in the files, get the timestamps, then return one interaction
	pos = [trajectory.tell() if trajectory != None else None for trajectory in f_preprocessed]
	lines = [trajectory.readline() if trajectory != None else None for trajectory in f_preprocessed]
	datapoints = [format_datapoint(line.split(',')) if line != None else None for line in lines]
	possible_timestamps = [datapoint[1] if datapoint != None else None for datapoint in datapoints]
	f_preprocessed = [trajectory.seek(pos[i]) if trajectory != None else None for i, trajectory in enumerate(f_preprocessed)]

	possible_timelines += [timestamp for timestamp in possible_timestamps if timestamp != None and timestamp > timeline]

	if (len(possible_timelines) != 0):
		# return the minimum timeline that has at least min_cluster trajectories behind it
		# if not possible, then return the max timeline
		possible_timelines.sort()
		if len(possible_timelines) >= min_cluster: return possible_timelines[min_cluster-1]
		else: return possible_timelines[-1]

	return timeline + timeline_rate


# A helper function to format a datapoint
def format_datapoint(datapoint):
	if datapoint == '': return None
	if datapoint == []: return None
	if datapoint == ['']: return None
	if datapoint == None: return None
	return [int(datapoint[0]), ciso8601.parse_datetime(datapoint[1]), float(datapoint[2]), float(datapoint[3])]


# A function to assign coordinates to clusters
def calc_cluster_coordinates(clusters_prev_timestamp, clusters_curr_timestamp, dict_clusters_prev_timestamp, dict_clusters_curr_timestamp):

	if(len(clusters_prev_timestamp) != 0):
		clusters = np.unique(clusters_prev_timestamp[:,-1])
		for cluster in clusters:
			if cluster == 0: continue
			coordinates = np.average(clusters_prev_timestamp[clusters_prev_timestamp[:,-1] == cluster][:,1:3], axis=0).tolist()
			dict_clusters_prev_timestamp[cluster] = [dict_clusters_prev_timestamp[cluster], coordinates]


	if(len(clusters_curr_timestamp) != 0):
		clusters = np.unique(clusters_curr_timestamp[:,-1])
		for cluster in clusters:
			if cluster == 0: continue
			coordinates = np.average(clusters_curr_timestamp[clusters_curr_timestamp[:,-1] == cluster][:,1:3], axis=0).tolist()
			dict_clusters_curr_timestamp[cluster] = [dict_clusters_curr_timestamp[cluster], coordinates]



