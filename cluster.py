import numpy as np
from sklearn.cluster import DBSCAN
import hdbscan
import geopy.distance

from constant import eps
from constant import min_samples

from math import radians, cos, sin, asin, sqrt

def dbscan(datapoints):

	if(datapoints.shape[0] < 2): return # cannot cluster a single trajectory

	#db = dbscan_oo(datapoints) # normal DBSCAN
	#db = dbscan_hn(datapoints) # DBSCAN with optimized haversine distance
	db = dbscan_hd(datapoints) # HDBSCAN

	return db


# The normal DBSCAN
def dbscan_oo(datapoints):

	db = DBSCAN(eps=eps, min_samples=min_samples, metric=dist).fit(datapoints)
	return db


# The DBSCAN algorithm with an optimized Haversine distance
def dbscan_hn(datapoints):

	n = len(datapoints)

	#Calculates the distance matrix
	lat1 = []
	lon1 = []
	lat2 = []
	lon2 = []

	for i in range(n):
		for j in range(n):
			lat1.extend(datapoints[i:i+1,0])
			lon1.extend(datapoints[i:i+1,1])
		lat2.extend(datapoints[:,0])
		lon2.extend(datapoints[:,1])

	distance = haversine_np(lat1, lon1, lat2, lon2).reshape((n,n))

	distance = np.ones(n*n).reshape((n,n))

	db = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed").fit(distance)

	return db


# The HDBSCAN algorithm

def dbscan_hd(datapoints):

	datapoints = [[39.88781, 116.36422],[39.88777, 116.36421]]

	clusterer = hdbscan.HDBSCAN(metric='haversine')
	clusterer.fit(datapoints)
	return clusterer







  # Distance Functions

def dist(coord_i, coord_j):

	# Geopy can calculate geodesic distance between two points using the:
	#		geodesic distance (default)
	#		great-circle distance (spherical model of Earth)
	#		vincenty distance (deprecated)
	# A free implementation of
	#		harversine (same as great-circle distance?)
	#
	# Sources
	# https://geopy.readthedocs.io/en/stable/
	# https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
	# https://stackoverflow.com/questions/29545704/fast-haversine-approximation-python-pandas

	return geodesic(coord_i, coord_j)
	# return great_circle(coord_i, coord_j)
	# return vincenty(coord_i, coord_j)
	# return haversine(coord_i, coord_j)
	# return test_dist(coord_i, coord_j)



def geodesic(coord_i, coord_j):
	return geopy.distance.distance(coord_i, coord_j).m  # Results are in meters

def great_circle(coord_i, coord_j):
	return geopy.distance.great_circle(coord_i, coord_j).m  # Results are in meters

def vincenty(coord_i, coord_j):
	return geopy.distance.vincenty(coord_i, coord_j).m  # Results are in meters

def test_dist(coord_i, coord_j):
	return 1



def haversine(coord_i, coord_j):

	lat1 = coord_i[0]
	lon1 = coord_i[1]

	lat2 = coord_j[0]
	lon2 = coord_j[1]


	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

	# haversine formula 
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a))
	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
	return c * r * 1000  # Results are in meters



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