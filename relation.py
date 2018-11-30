import constant
from constant import min_shared
from constant import lifecycle_dir
from constant import file_suffix
from constant import NO_CLUSTER

import numpy as np
from datetime import datetime

# relations
NO_RELATION = -1

SAME     = 0

T_ENTER  = 10
C_ENTER  = 11

T_LEAVE  = 20
C_LEAVE  = 21

MERGE    = 3
SPLIT    = 4

START    = 5
END      = 6

CLUSTER_RELATIONS = [NO_RELATION, SAME, C_ENTER, C_LEAVE, MERGE, SPLIT, START, END]
TRAJ_RELATIONS = [T_ENTER, T_LEAVE]

# Relations TEXT
START_TXT = 'starts'


# Checks if c1 and c2 are the same cluster according to the minShared percentage
def is_same(c1, c2):

	n_c1 = float(len(c1))
	n_c2 = float(len(c2))
	if n_c1 == 0 or n_c2 == 0: return False
	n_intersect = float(len([traj for traj in c1 if traj in c2]))

	if n_intersect / n_c1 >= min_shared and n_intersect / n_c2 >= min_shared:
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


	# Associates trajectories to clusters, and organize by cluster, on previous timestamp
	# Note the 'traj' at the dictionary name
	n_clusters_prev_timestamp = 0
	cluster_list_prev = []
	if len(clusters_prev_timestamp) > 0:
		cluster_list_prev = np.unique(clusters_prev_timestamp[clusters_prev_timestamp.dtype.names[-1]])
		cluster_list_prev = np.delete(cluster_list_prev, np.where(cluster_list_prev == NO_CLUSTER)) # removes (NO_CLUSTER)
		n_clusters_prev_timestamp = cluster_list_prev.size
	dict_traj_prev_timestamp = {k: [] for k in cluster_list_prev} 
	if n_clusters_prev_timestamp > 0: # accounts for the timestamp in which all trajectories do not belong to any cluster
		for traj in clusters_prev_timestamp:
			dict_traj_prev_timestamp[traj[-1]].append(traj[0]) # appends id to the entry of a specific cluster in the dictionary

	# Associates trajectories to clusters, and organize by cluster, on current timestamp
	# Note the 'traj' at the dictionary name
	n_clusters_curr_timestamp = 0
	cluster_list_curr = []
	if len(clusters_curr_timestamp) > 0:
		cluster_list_curr = np.unique(clusters_curr_timestamp[clusters_curr_timestamp.dtype.names[-1]])
		cluster_list_curr = np.delete(cluster_list_curr, np.where(cluster_list_curr == NO_CLUSTER)) # removes (NO_CLUSTER)
		n_clusters_curr_timestamp = cluster_list_curr.size
	dict_traj_curr_timestamp = {k: [] for k in cluster_list_curr} 
	if n_clusters_curr_timestamp > 0: # accounts for the timestamp in which all trajectories do not belong to any cluster
		for traj in clusters_curr_timestamp:
			dict_traj_curr_timestamp[traj[-1]].append(traj[0]) # appends id to the entry of a specific cluster in the dictionary




	# Create dictionary of clusters x clusters for previous and current timestamps
	# Note the 'cluster' at the dictionary name
	dict_cluster_prev_timestamp = {k: [] for k in cluster_list_prev}
	dict_cluster_curr_timestamp = {k: [] for k in cluster_list_curr}

	# Populate dictionaries with their relations with other clusters

	individual_traj_enter = dict_traj_curr_timestamp.copy()

	for cluster_prev in dict_traj_prev_timestamp:

		individual_traj_leave = list(dict_traj_prev_timestamp[cluster_prev])

		for cluster_curr in dict_traj_curr_timestamp:

			# Intersection of lists
			common_traj = [traj for traj in dict_traj_prev_timestamp[cluster_prev] if traj in dict_traj_curr_timestamp[cluster_curr]]

			# Eliminates trajectories we know went to another cluster
			individual_traj_leave = np.setdiff1d(individual_traj_leave, common_traj)
			# Eliminates trajectories we know came from another cluster
			individual_traj_enter[cluster_curr] = np.setdiff1d(individual_traj_enter[cluster_curr], common_traj)


			# Associates cluster who share elements
			if len(common_traj) > 0:

				# Calculate cross temporal cluster similarity
				if is_same(dict_traj_prev_timestamp[cluster_prev], dict_traj_curr_timestamp[cluster_curr]):
					dict_cluster_prev_timestamp[cluster_prev].append([cluster_curr, SAME])
					dict_cluster_curr_timestamp[cluster_curr].append([cluster_prev, SAME])
				else:
					dict_cluster_prev_timestamp[cluster_prev].append([cluster_curr, NO_RELATION])
					dict_cluster_curr_timestamp[cluster_curr].append([cluster_prev, NO_RELATION])



		# Marks individual trajectories that left the cluster
		for traj in individual_traj_leave:
			dict_cluster_prev_timestamp.append([traj, T_LEAVE])
				

	# mark individual trajectories that entered the cluster
	for cluster_curr in individual_traj_enter:
		for traj in individual_traj_enter[cluster_curr]:
			dict_cluster_curr_timestamp[cluster_curr].append([traj, T_ENTER])


	# At this point, potential cluster or trajectory enters and leaves are marked.
	# Further analysis will associate same clusers in different timestamps and mark trajectories that continued in the cluster.

	return dict_cluster_prev_timestamp, dict_cluster_curr_timestamp





# def calc_similarity(dict_cluster_prev_timestamp, dict_cluster_curr_timestamp):


# 	# cluster_list_prev = []
# 	# if len(clusters_prev_timestamp) > 0:
# 	# 	cluster_list_prev = np.unique(clusters_prev_timestamp[:,-1:]).astype(np.int32) # np.int32 required to avoid warning
# 	# 	cluster_list_prev = np.delete(cluster_list_prev, np.where(cluster_list_prev == NO_CLUSTER)) # removes (NO_CLUSTER)

# 	# cluster_list_curr = []
# 	# if len(clusters_curr_timestamp) > 0:
# 	# 	cluster_list_curr = np.unique(clusters_curr_timestamp[:,-1:]).astype(np.int32) # np.int32 required to avoid warning
# 	# 	cluster_list_curr = np.delete(cluster_list_curr, np.where(cluster_list_curr == NO_CLUSTER)) # removes (NO_CLUSTER)



# 	dict_cross_cluster = {} # keys: current ids / values: previous ids -- useful when updating current ids later on

# 	print('---------------------------------------------------------')
# 	print(dict_cluster_prev_timestamp)
# 	print(dict_cluster_curr_timestamp)



# 	for cluster_curr in dict_cluster_curr_timestamp:
# 		for cluster_prev in [c_prev[0] for c_prev in dict_cluster_curr_timestamp[cluster_curr] if c_prev[1] in CLUSTER_RELATIONS]: # only check ids of clusters curr_cluster has relations with
# 			if is_same( [c_prev[0] for c_prev in dict_cluster_prev_timestamp[cluster_prev] if c_prev[1] in TRAJ_RELATIONS],[c_curr[0] for c_curr in dict_cluster_curr_timestamp[cluster_curr] if c_curr[1] in TRAJ_RELATIONS] ):
# 				if cluster_curr[0] in dict_cross_cluster.keys():
# 					raise ValueError('Cluster ' + str(cluster_curr[0]) + ' already exists in the dictionary, and therefore has already been associated with another cluster.')
# 				else:
# 					dict_cross_cluster[cluster_curr[0]] = cluster_prev[0]


# 	return dict_cross_cluster

	


def calc_cluster_id(clusters_prev_timestamp, clusters_curr_timestamp, dict_cluster_prev_timestamp, dict_cluster_curr_timestamp):


	# Checks the cross matrix to identify current clusters that did not exist in the past
	# internal_cluster_ids = [cluster_id for cluster_id in dict_clusters_curr_timestamp.keys() if cluster_id not in dict_cross_cluster]
	# print('new_cluster_ids')
	# print(internal_cluster_ids)

	# # Assign a new universal cluster id to these clusters
	# # Negative cluster ids are internal, positive cluster ids are universal
	# dict_internal_universal_cluster_ids = {}
	# for internal_cluster_id in internal_cluster_ids:
	# 	dict_internal_universal_cluster_ids[internal_cluster_id] = constant.cluster_id_counter
	# 	constant.cluster_id_counter += 1


	# Identify new clusters by looking for clusters without a IS_SAME relation
	# Assign an universal id to new clusters
	# Store results in a list for later updates

	dict_update_cluster = {} # internal id: universal id

	for cluster_curr in dict_cluster_curr_timestamp:
		exists_before = False
		for cluster_prev in dict_cluster_curr_timestamp[cluster_curr]:
			if cluster_prev[1] == SAME:
				exists_before = True
				if cluster_curr != cluster_prev[0]:
					dict_update_cluster[cluster_curr] = cluster_prev[0]
				break
		if not exists_before:
			dict_update_cluster[cluster_curr] = constant.cluster_id_counter
			constant.cluster_id_counter += 1


	



	# Updates data structures with new universal cluster ids

	print('---------------------------------------------------------------------')
	print(dict_update_cluster)

	print('before update')
	print(clusters_prev_timestamp)
	print(clusters_curr_timestamp)
	print(dict_cluster_prev_timestamp)
	print(dict_cluster_curr_timestamp)

	for internal_cluster_id in dict_update_cluster.keys():
		# clusters_prev_timestamp[:,-1] = [dict_update_cluster[internal_cluster_id] if cluster_id == internal_cluster_id else cluster_id for cluster_id in clusters_prev_timestamp[:,-1]]
		# clusters_curr_timestamp[:,-1] = [dict_update_cluster[internal_cluster_id] if cluster_id == internal_cluster_id else cluster_id for cluster_id in clusters_curr_timestamp[:,-1]]
		clusters_prev_timestamp['cid'][clusters_prev_timestamp['cid']==internal_cluster_id] = dict_update_cluster[internal_cluster_id]
		clusters_curr_timestamp['cid'][clusters_curr_timestamp['cid']==internal_cluster_id] = dict_update_cluster[internal_cluster_id]


	for internal_cluster_id in dict_cluster_prev_timestamp:
		# update values first
		for cluster_id in dict_cluster_prev_timestamp[internal_cluster_id]:
			if cluster_id[0] in dict_update_cluster.keys():
				cluster_id[0] = dict_update_cluster[internal_cluster_id]
		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_prev_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_prev_timestamp.pop(internal_cluster_id)


	for internal_cluster_id in dict_cluster_curr_timestamp:
		# update values first
		for cluster_id in dict_cluster_curr_timestamp[internal_cluster_id]:
			if cluster_id[0] in dict_update_cluster.keys():
				cluster_id[0] = dict_update_cluster[internal_cluster_id]
		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_curr_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_curr_timestamp.pop(internal_cluster_id)


	print('after update')
	print(clusters_prev_timestamp)
	print(clusters_curr_timestamp)
	print(dict_cluster_prev_timestamp)
	print(dict_cluster_curr_timestamp)


	# cluster_prev_timestamp
	#for c in cluster_prev_timestamp

	


	###################################################################################################################
	# Message to myself
	# Should update other variables
	# Note that you changed how cluster ids work
	# Cluster ids returned by DBSCAN (called internal) start in zero (NO CLUSTER) and are *** NEGATIVE ***
	# Universal cluster ids (those that you will save in files) are positive
	# You are buliding a conversion dictionary
	# For some reason, some of these ids are in string format. Double-check if they are ints... if needed.
	# I tried to fix that, but I think that a past me decided to keep it text for some reason... :/
	#################################################################################################################

	# Updates cluster ids

	# print('before update')
	# print(clusters_curr_timestamp)


	# print('after update')
	# print(clusters_curr_timestamp)




	# Updates clusters_curr_timestamp with universal cluster ids.
	# for cluster_id in cluster_list_curr:
	# 	if cluster_id in dict_cross_cluster.keys():
	# 		print(cluster_id)
	# 		print(clusters_curr_timestamp)
	# 		np.where(clusters_curr_timestamp[0] == cluster_id)
	# 		print(np.where(clusters_curr_timestamp == cluster_id))
	# 		#clusters_curr_timestamp[np.where(clusters_curr_timestamp == cluster_id)] = dict_cross_cluster[cluster_id]


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


