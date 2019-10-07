import sys

#####
#
# TODO: DIVIDE THIS INTO CONSTANTS AND CONFIGURATIONS
#
#####

original_dir     = './originals/'
preprocessed_dir = './preprocessed/' # must be manually created before execution
lifecycle_dir    = './lifecycle/'    # must be manually created before execution

if len(sys.argv) > 3:
	original_dir     = sys.argv[1]
	preprocessed_dir = sys.argv[3]


file_suffix = '.txt'


# Parameters
min_cluster = 4
min_shared  = 0.8

if len(sys.argv) > 3:
	min_cluster = int(sys.argv[2])


# Process
rate = 1 # minutes


'''Cluster'''
cluster_id_counter = 1
NO_CLUSTER = 0


# DBSCAN
eps = 50  # (in meters) The maximum distance between two samples for them
					  # to be considered as in the same neighborhood.
min_samples = min_cluster  # The number of samples (or total weight) in a neighborhood
													 # for a point to be considered as a core point. This includes the point itself.