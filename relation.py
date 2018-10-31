import constant
from constant import min_shared
from constant import lifecycle_dir
from constant import file_suffix

import numpy as np
from datetime import datetime

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
	else: return False


def save_start(old_id, new_id, timestamp, clusters):
	f = open(lifecycle_dir + new_id + file_suffix, 'w')
	f.write(timestamp + ": " + new_id + " " + START_TXT)




def calc_relations(clusters_prev_timestamp, clusters_curr_timestamp):

	########
	#  IF PREV_TIMESTAMP IS EMPTY -> START RELATION ON CURR-TIMESTAMP
	########


	# Associates trajectories to clusters, and organize by cluster, on previous timestamp
	n_clusters_prev_timestamp = 0
	if len(clusters_prev_timestamp) > 0:
		n_clusters_prev_timestamp = np.unique(clusters_prev_timestamp[:,-1:]).size - (1 if -1 in clusters_prev_timestamp[:,-1:] else 0)
	dict_traj_prev_timestamp = {k: [] for k in range(n_clusters_prev_timestamp)}
	for traj in clusters_prev_timestamp:
		dict_traj_prev_timestamp[int(traj[-1])].append(traj[0])

	# Associates trajectories to clusters, and organize by cluster, on current timestamp
	n_clusters_curr_timestamp = 0
	if len(clusters_curr_timestamp) > 0:
	  n_clusters_curr_timestamp = np.unique(clusters_curr_timestamp[:,-1:]).size - (1 if -1 in clusters_curr_timestamp[:,-1:] else 0)
	dict_traj_curr_timestamp = {k: [] for k in range(n_clusters_curr_timestamp)}
	for traj in clusters_curr_timestamp:
		dict_traj_curr_timestamp[int(traj[-1])].append(traj[0])


	# Create dictionary of clusters x clusters for previous and current timestamps
	dict_cluster_prev_timestamp = {k: [] for k in range(n_clusters_prev_timestamp)}
	dict_cluster_curr_timestamp = {k: [] for k in range(n_clusters_curr_timestamp)}

	# Populate dictionaries with their relatiosn with other clusters
	# TODO: Must be improved to include individual trajectories
	for cluster_prev in dict_traj_prev_timestamp:
		for cluster_curr in dict_traj_curr_timestamp:
			if len(dict_traj_prev_timestamp[cluster_prev] & dict_traj_curr_timestamp[cluster_curr]) > 0:
				dict_cluster_prev_timestamp.append([cluster_curr, NO_RELATION])
				dict_cluster_curr_timestamp.append([cluster_prev, NO_RELATION])


	# Process clusters in the previous timestamp (i.e. looking for leave relationships)
	for cluster_prev in dict_cluster_prev_timestamp:
		dict_cluster_prev_timestamp[cluster_prev] = [[cluster[0], SAME] if is_same(dict_traj_prev_timestamp[cluster_prev], dict_traj_curr_timestamp[cluster]) else [cluster[0], LEAVE] for cluster in dict_cluster_prev_timestamp[cluster_prev]]

	# Process clusters in the current timestamp (i.e. looking for enter relationships)
	for cluster_curr in dict_cluster_curr_timestamp:
		dict_cluster_curr_timestamp[cluster_curr] = [[cluster[0], SAME] if is_same(dict_traj_curr_timestamp[cluster_prev], dict_traj_prev_timestamp[cluster]) else [cluster[0], ENTER] for cluster in dict_cluster_curr_timestamp[cluster_curr]]

	return dict_cluster_prev_timestamp, dict_cluster_curr_timestamp


def save_relations(dict_cluster_prev_timestamp, dict_cluster_curr_timestamp, prev_timestamp, curr_timestamp):

	new_clusters = {} # stores new clusters

	# Process Start relations
	for cluster_curr in dict_cluster_curr_timestamp:
		if is_start(dict_cluster_curr_timestamp[cluster_curr]):
			new_cluster_id = constant.cluster_id_counter
			constant.cluster_id_counter += 1
			save_start(cluster_curr, new_cluster_id, curr_timestamp, dict_cluster_curr_timestamp[cluster_curr])
			new_clusters[cluster_curr] = new_cluster_id

	# Process Leave / Split relations
	#for 

	# Process Enter / Merge
	#for

	# Process End relations
	#for



def save_start(old_id, new_id, timestamp, clusters):
	f = open(lifecycle_dir + str(new_id) + file_suffix, 'w')
	s = ''
	for cluster in clusters:
		s += cluster + ', '
	timestamp_str = datetime.strftime(timestamp, '%d %H:%M')
	f.write(timestamp_str + ': ' + str(new_id) + ' ' + START_TXT + '(' + s + ').')


