from datetime import datetime
from datetime import timedelta

from constant import original_dir
from constant import preprocessed_dir
from constant import rate
from file import identify_trajectories

from cluster import dbscan

from relation import calc_relations
from relation import calc_cluster_id
from relation import save_relations

import numpy as np
from numpy.lib.recfunctions import append_fields

import time
import ciso8601


## Pre process files.
## Removes year, month, day, second, and microsecond from datestamps

def preprocess():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:
			
			datapoint = line.split(',')
			_id        = datapoint[0]
			_timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S')
			_lat       = datapoint[3][0:-2] if '\n' in datapoint[3] else datapoint[3]  # removes '\n'
			_lon       = datapoint[2]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()


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

		datapoints_valid = np.array([(datapoints[i][0], datapoints[i][2], datapoints[i][3]) for i, timestamp in enumerate(timestamps) if timestamp != None and timeline >= timestamp])

		clusters_curr_timestamp = datapoints_valid[:,1:].copy() # get lats and longs
		labels = dbscan(clusters_curr_timestamp) # performs dbscan and get labels
		clusters_curr_timestamp = np.zeros((datapoints_valid.shape[0],datapoints_valid.shape[1]+1)) # adds a column
		clusters_curr_timestamp[:,:-1] = datapoints_valid
		clusters_curr_timestamp[:,-1:] = np.array([labels]).transpose()
		clusters_curr_timestamp[:,-1:] = clusters_curr_timestamp[:,-1:]*-1-1  # so traj without clusters have cluster id zero, internal are negative, external are positive



		# Calculate Relations
		dict_clusters_prev_timestamp, dict_clusters_curr_timestamp = calc_relations(clusters_prev_timestamp, clusters_curr_timestamp)

		# Assign universal cluster ids and update cluster ids
		calc_cluster_id(clusters_prev_timestamp, clusters_curr_timestamp, dict_clusters_prev_timestamp, dict_clusters_curr_timestamp)

		# Save Relations
		save_relations(dict_clusters_prev_timestamp, dict_clusters_curr_timestamp, timeline-timeline_rate, timeline)


		# Updates for next iteration: timeline, and cluster list
		timeline = timeline + timeline_rate
		clusters_prev_timestamp = np.copy(clusters_curr_timestamp)


	for file in f_preprocessed:
		file.close()




# A helper function in process()
# Given a trajectory (file), find the timestamp (line) just before the universal timeline
# A trajectory and a datapoint have to be passed because, in some cases, the algorithm needs to give one step back
def calculate_next_datapoint(traj, tl, tl_rate, prev_datapoint):

	# Already reached EOF
	if prev_datapoint is None: return None

	# Checks if needs to update
	if prev_datapoint[1] >= tl: return prev_datapoint

	# Tries to update
	pos = traj.tell()
	curr_datapoint = prev_datapoint

	# Timeline is always set, use it
	while True:
		line = traj.readline()
		if line == '': break # EOF
		if ciso8601.parse_datetime(line.split(',')[1]) > tl:
			traj.seek(pos)
			return curr_datapoint
		pos = traj.tell()
		curr_datapoint = format_datapoint(line.split(','))

	# If the timestamp I have is old, then do not use it. It has been processed already
	if (tl - curr_datapoint[1]) >= tl_rate:
		return None
	else:
		return curr_datapoint


# A helper function to format a datapoint
def format_datapoint(datapoint):
	if datapoint == []: return []
	if datapoint == None: return None
	return [int(datapoint[0]), ciso8601.parse_datetime(datapoint[1]), float(datapoint[2]), float(datapoint[3])]







