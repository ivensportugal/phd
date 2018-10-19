# Files
small_original_dir  = './originals/'
medium_original_dir = './originals_medium/'
large_original_dir  = './originals_all/'

original_dir     = small_original_dir
preprocessed_dir = 'preprocessed/'
lifecycle_dir    = 'lifecycle/'

file_suffix = '.txt'


# Parameters
min_cluster = 3
min_shared  = 0.8


# Process
rate = 10 #minutes


# Cluster
cluster_id_counter = 0


# DBSCAN
eps = 6000  # (in seconds) The maximum distance between two samples for them
					  # to be considered as in the same neighborhood.
min_samples = min_shared  # The number of samples (or total weight) in a neighborhood
													# for a point to be considered as a core point. This includes the point itself.