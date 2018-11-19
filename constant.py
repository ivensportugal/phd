#####
#
# TODO: DIVIDE THIS INTO CONSTANTS AND CONFIGURATIONS
#
#####


# Files
small_original_dir  = './originals/'
medium_original_dir = './originals_medium/'
large_original_dir  = './originals_all/'
test_original_dir   = './originals_test/'

original_dir     = test_original_dir
preprocessed_dir = 'preprocessed/'
lifecycle_dir    = 'lifecycle/'

file_suffix = '.txt'


# Parameters
min_cluster = 2
min_shared  = 0.8


# Process
rate = 1 # minutes


'''Cluster'''
cluster_id_counter = 0


# DBSCAN
eps = 200  # (in meters) The maximum distance between two samples for them
					  # to be considered as in the same neighborhood.
min_samples = min_cluster  # The number of samples (or total weight) in a neighborhood
													 # for a point to be considered as a core point. This includes the point itself.