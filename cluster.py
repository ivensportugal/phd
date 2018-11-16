import numpy as np
from sklearn.cluster import DBSCAN
import geopy.distance

from constant import eps
from constant import min_samples

def dbscan(datapoints):

  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  if(datapoints.size == 0): return
  db = DBSCAN(eps=eps, min_samples=min_samples, metric=dist).fit(datapoints)

  return db



  # Distance Functions

def dist(coord_i, coord_j):

	# Euclidean Distance
	return euclidean_distance_1(coord_i, coord_j)

	# Another Distance
	#return another_value



def euclidean_distance_1(coord_i, coord_j):
	return geopy.distance.vincenty(coord_i, coord_j).m  # Results are in meters
