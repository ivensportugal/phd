import numpy
import geopy.distance

# Constants
r_e = 5		# meters
r_n = 30	# meters


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

