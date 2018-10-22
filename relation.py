from constant import min_shared
from constant import cluster_id_counter
from constant import lifecycle_dir
from constant import file_suffix

# relations
NO_RELATION = -1

SAME   = 0

ENTER  = 1
LEAVE  = 2
MERGE  = 3
SPLIT  = 4
START  = 5
END    = 6

# Relations TEXT
START_TXT = 'starts'


# Checks if c1 and c2 are the same cluster according to minShared percentage
def is_same(c1, c2):
	n_c1 = float(len(c1))
	n_c2 = float(len(c2))
	n_intersect = float(len(c1 & c2))

	if n_interset / n_c1 >= min_shared and n_intersect / n_c2 >= min_shared:
		return True
	else:
		return False

# Checks if a cluster starts existing based on the clusters it has relationships with
def is_start(clusters):
	if all(c[-1] != SAME for c in clusters): return True
	else return False


def save_start(old_id, new_id, timestamp, clusters):
	f = open(lifecycle_dir + new_id + file_suffix, 'w')
	f.write(timestamp + ": " + new_id + " " START_TXT)




def calc_relations(clusters_prev_timestamp, clusters_curr_timestamp):

	########
	#  IF PREV_TIMESTAMP IS EMPTY -> START RELATION ON CURR-TIMESTAMP
	########

	# Associates trajectories to clusters, and organize by cluster, on previous timestamp
	n_clusters_prev_timestamp = len(set(clusters_prev_timestamp)) - (1 if -1 in clusters_prev_timestamp else 0)
	dict_traj_prev_timestamp = {k: [] for k in range(n_clusters_prev_timestamp)}
	last_column = clusters_prev_timestamp.shape[clusters_prev_timestamp.ndim-1]-1
	for traj in clusters_prev_timestamp:
		dict_traj_prev_timestamp[traj[last_column]].append(traj[0])

	# Associates trajectories to clusters, and organize by cluster, on current timestamp
	n_clusters_curr_timestamp = len(set(clusters_curr_timestamp)) - (1 if -1 in clusters_curr_timestamp else 0)
	dict_traj_curr_timestamp = {k: [] for k in range(n_clusters_curr_timestamp)}
	last_column = clusters_curr_timestamp.shape[clusters_curr_timestamp.ndim-1]-1
	for traj in clusters_curr_timestamp:
		dict_traj_curr_timestamp[traj[last_column]].append(traj[0])


	# Create dictionary of clusters x clusters for previous and current timestamps
	dict_cluster_prev_timestamp = {k: [] for k in range(n_clusters_prev_timestamp)}
	dict_cluster_curr_timestamp = {k: [] for k in range(n_clusters_curr_timestamp)}

	for cluster_prev in dict_traj_prev_timestamp:
		for cluster_curr in dict_traj_curr_timestamp:
			if len(dict_traj_prev_timestamp[cluster_prev] & dict_traj_curr_timestamp[cluster_curr]) > 0:
				dict_cluster_prev_timestamp.append([cluster_curr, NO_RELATION])
				dict_cluster_curr_timestamp.append([cluster_prev, NO_RELATION])


	# Process clusters in the previous timestamp (i.e. looking for leave relationships)
	for cluster_prev in dict_cluster_prev_timestamp:
		dict_cluster_prev_timestamp[cluster_prev] = [if is_same(dict_traj_prev_timestamp[cluster_prev], dict_traj_curr_timestamp[cluster]) [cluster[0], SAME] else [cluster[0], LEAVE] for cluster in dict_cluster_prev_timestamp[cluster_prev]]

	# Process clusters in the current timestamp (i.e. looking for enter relationships)
	for cluster_prev in dict_cluster_curr_timestamp:
		dict_cluster_curr_timestamp[cluster_curr] = [if is_same(dict_traj_curr_timestamp[cluster_prev], dict_traj_prev_timestamp[cluster]) [cluster[0], SAME] else [cluster[0], ENTER] for cluster in dict_cluster_curr_timestamp[cluster_curr]]

	return dict_cluster_prev_timestamp, dict_cluster_curr_timestamp


def save_relations(dict_cluster_prev_timestamp, dict_cluster_curr_timestamp, prev_timestamp, curr_timestamp):

	new_clusters = {} # stores new clusters

	# Process Start relations
	for cluster_curr in dict_cluster_curr_timestamp:
		if is_start(dict_cluster_curr_timestamp[cluster_curr]):
		  new_cluster_id = cluster_id_counter
		  cluster_id_counter += 1
		  save_start(cluster_curr, new_cluster_id, , curr_timestamp, dict_cluster_curr_timestamp[cluster_curr])
		  new_clusters[cluster_curr] = new_cluster_id

	# Process Leave / Split relations
	for 

	# Process Enter / Merge
	for

	# Process End relations
	for



def save_start(old_id, new_id, timestamp, clusters):
	f = open(lifecycle_dir + new_id + file_suffix, 'w')
	s = ''
	for cluster in clusters:
		s += cluster + ', '
	f.write(timestamp + ': ' + new_id + START_TXT + '(' + s + ').')


