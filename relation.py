from constant import min_cluster
from constant import min_shared

# relations
NO_RELATION = -1

SAME   = 0

ENTER  = 1
LEAVE  = 2
MERGE  = 3
SPLIT  = 4
START  = 5
END    = 6



def calc_relations(clusters_curr_timestamp, clusters_prev_timestamp):

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
				dict_cluster_prev_timestamp.append([cluster_curr,NO_RELATION])
				dict_cluster_curr_timestamp.append([cluster_prev,NO_RELATION])





