import sys

#####
#
# TODO: DIVIDE THIS INTO CONSTANTS AND CONFIGURATIONS
#
#####

original_dir      	  = '../process/originals/'
preprocessed_dir  	  = '../process/preprocessed/'  	# must be manually created before execution

cluster_dir       	  = '../process/cluster/'       	# must be manually created before execution
preprocessed2_dir 	  = '../process/preprocessed2/' 	# must be manually created before execution
# lifecycle_dir     = '../process/lifecycle/'

preprocessedneo4j_dir = '../process/preprocessedneo4j/' 	# must be manually created before execution
nodes_filename        = 'nodes.csv'
edges_filename        = 'edges.csv'


if len(sys.argv) > 3:
	original_dir     = sys.argv[1]
	preprocessed_dir = sys.argv[3]


file_suffix = '.txt'


# Parameters
min_cluster = 3
min_shared  = 0.8

if len(sys.argv) > 3:
	min_cluster = int(sys.argv[2])


# Process
rate = 1 # minutes


# Cluster
cluster_id_counter = 1
NO_CLUSTER = 0


# Neo4J
NODES_HEADER = 'clusterId,size,timestamp\n'
EDGES_HEADER = 'clusterIdBefore,clusterIdAfter,timestampBefore,timestampAfter,clusterRelationship\n'



# DBSCAN
eps = 40  # (in meters) The maximum distance between two samples for them
					  	# to be considered as in the same neighborhood.
min_samples = min_cluster # The number of samples (or total weight) in a neighborhood
							# for a point to be considered as a core point. This includes the point itself.
