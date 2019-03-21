import numpy as np
# from sklearn.cluster import DBSCAN
import os
from datetime import datetime
from datetime import timedelta

import ciso8601

def dbscan(datapoints):

  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  if(datapoints.size == 0): return
  db = DBSCAN(eps=200, min_samples=3, metric="precomputed").fit(datapoints)

  return db


def haversine_np(lat1, lon1, lat2, lon2):


	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

	# haversine formula 
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
	c = 2 * np.arcsin(np.sqrt(a))
	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
	return c * r * 1000  # Results are in meters


# datapoints = np.array([(39.92123, 116.51172), (39.88781, 116.36422)])

# lat1 = np.array([39.92123, 39.92123, 39.88781, 39.88781])
# lon1 = np.array([116.51172, 116.51172, 116.36422, 116.36422])
# lat2 = np.array([39.92123, 39.88781, 39.92123, 39.88781])
# lon2 = np.array([116.51172, 116.36422, 116.51172, 116.36422])


# for i in range(1):
# 	distance = haversine_np(lat1, lon1, lat2, lon2)
# m = distance.reshape((2,2))

# print(m)
# db = dbscan(m)

# print(db).labels_


def identify_trajectories(dir):
  files = []
  for file in os.listdir(dir):
    if file.endswith(file_suffix):
      files.append(file)
  return files

def format_datapoint(datapoint):
	if datapoint == []: return []
	if datapoint == None: return None
	return [int(datapoint[0]), datetime.strptime(datapoint[1], '%d %H:%M'), float(datapoint[2]), float(datapoint[3])]


preprocessed_dir = 'preprocessed_90/'
file_suffix = '.txt'
rate = 1


trajectories = identify_trajectories(preprocessed_dir)

f_preprocessed = [open(preprocessed_dir + trajectory, 'r') for trajectory in  trajectories]
while(True):
	lines           = [file.readline()             for file      in f_preprocessed ]
	datapoints_temp = [l.split(',')                for l         in lines          ]
	datapoints      = [format_datapoint(datapoint) for datapoint in datapoints_temp if datapoint[0] != '']
	if all(datapoint == '' for datapoint in datapoints): break

# datapoints = [format_datapoint(trajectory.readline().split(',')) for trajectory in f_preprocessed] # starting datapoints, assumes files contain data, [[int, time, float, float]]
# timestamps = [datapoint[1] for datapoint in datapoints] # the first timestamp of every file, assumes files contain data

# timeline = min(timestamps) # The universal timeline
# timeline_rate = timedelta(minutes=rate)


# clusters_curr_timestamp = np.array([], dtype=[('tid','i4'),('lat','f4'),('lon','f4'),('cid','i4')]) # 'tid', 'lat', 'lon', 'cid' <- these are labels - int, float, float, int
# clusters_prev_timestamp = np.array([], dtype=[('tid','i4'),('lat','f4'),('lon','f4'),('cid','i4')]) # 'tid', 'lat', 'lon', 'cid' <- these are labels - int, float, float, int

# j = 0
# while(j < 100):
# 	datapoints = [(trajectory, timeline, timeline_rate, datapoints[i]) for i, trajectory in enumerate(f_preprocessed)]
# 	print(i)
# 	j += 1
