import numpy
import geopy.distance

# Relations
r_e = 5		# meters
r_n = 30	# meters


# Clustering

eps = 12000  # (in seconds) The maximum distance between two samples for them
					 # to be considered as in the same neighborhood.
min_samples = 2  	# The number of samples (or total weight) in a neighborhood
									# for a point to be considered as a core point. This includes the point itself.





# File structure

file_suffix = '.txt'

original_dir = './originals/'
processed_a_dir = './processed_a/'
processed_r_dir = './processed_r/'

processed_prefix = 'p'




# Distance Functions

def dist(coord_i, coord_j):

	# Euclidean Distance
	return euclidean_distance_1(coord_i, coord_j)

	# Another Distance
	#return another_value



def euclidean_distance_1(coord_i, coord_j):
	return geopy.distance.vincenty(coord_i, coord_j).m  # Results are in meters

