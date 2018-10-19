from datetime import datetime
from datetime import timedelta

from constant import original_dir
from constant import preprocessed_dir
from constant import rate
from io import identify_trajectories


## Pre process files.
## Removes year, month, day, second, and microsecond from datestamps

def preprocess():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original  = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:
			
			datapoint = line.split(',')
			_id        = datapoint[0]
			_timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S')
			_lat       = datapoint[3][0:-2]
			_lon       = datapoint[2]

			newline = _id + ',' + _timestamp.strftime('%d %H:%M') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()


## Process trajectories.
## Identify clusters, store their lifecycle

def process():

	trajectories = identify_trajectories(preprocessed_dir)
	f_preprocessed = []
	for trajectory in trajectories:
		f_preprocessed.append(open(preprocessed_dir + trajectory, 'r'))


	timeline = None
	timeline_rate = datapoint
	has_trajectory = true

	clusters_curr_timestamp = []
	clusters_prev_timestamp = []

	while(has_trajectory):
		has_trajectory = false

		# Read all trajectories
		lines = [trajectory.readline() for trajectory in f_preprocessed]

		# Stop Condition: If all files have been read, stop
		if all(line == '' for line in lines): break

		# Process each line, so its possible to access data
		datapoints = [line.split(',') for line in lines]
		timestamps = [datetime.strptime(datapoint[1], '%d %H:%M') if datapoint != '' else datetime.max for datapoint in datapoints]

		# Start timeline if needed
		if not timeline;
			timeline = min(timestamps)

		# Performs one hop, so valid data points are less than timeline
		timeline = timeline + datetime(minutes=rate)

		# Performs DBSCAN only on those points that are valid (less than universal timestamp)
		datapoints_valid = np.array([[datapoints[i][0], datapoints[i][2], datapoints[i][3]] if (timeline - timestamp).total_seconds() >= 0 for i, timestamp in enumerate(timestamps)])
		last_column = datapoints_valid.shape[datapoints_valid.ndim-1]-1
		clusters_curr_timestamp = np.insert(datapoints_valid, last_column+1, dbscan(datapoints_valid[:,2,4]).labels_, axis=1)

		dict_clusters_prev_timestamp, dict_clusters_curr_timestamp = calc_relations(clusters_prev_timestamp, clusters_curr_timestamp)
		save_relations(dict_clusters_prev_timestamp, dict_clusters_curr_timestamp, timestamp-datetime(minutes=rate), timeline)



		has_trajectory = any(datapoint != '' for datapoint in datapoints)


	for file in f_preprocessed:
		file.close()




