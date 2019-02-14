import constant
from constant import min_shared
from constant import min_cluster
from constant import lifecycle_dir
from constant import file_suffix
from constant import NO_CLUSTER

import numpy as np
from datetime import datetime

# relations
NO_RELATION = -1

SAME     = 00

START    = 10
END      = 11

T_ENTER  = 20
T_LEAVE  = 21

C_IN     = 30
C_OUT    = 31

C_ENTER  = 40
C_LEAVE  = 41

GROUP    = 50
DISPERSE = 51

MERGE    = 60
SPLIT    = 61




# Relations TEXT
START_TXT = 'starts'


# Checks if c1 and c2 are the same cluster according to the minShared percentage
def is_same(c1, c2, c1_leave, c2_enter, common):

	n_c1 = float(len(c1))
	n_c2 = float(len(c2))
	n_c1_leave = float(len(c1_leave))
	n_c2_enter = float(len(c2_enter))
	n_common = float(len(common))

	if n_c1      == 0: return False
	if n_c2      == 0: return False
	if n_common  == 0: return False

	if n_common / (n_c1 - n_c1_leave) >= min_shared and n_common / (n_c2 - n_c2_enter) >= min_shared:
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




	# Identifies individual trajectories that leave or enter

	
	individual_traj_leave = dict_traj_prev_timestamp.copy() # List of trajectories that LEAVE the cluster (no cluster id in the next timestamp)
	individual_traj_enter = dict_traj_curr_timestamp.copy() # List of trajectories that ENTER the cluster (no cluster id in the prev timestamp)

	for cluster_prev in dict_traj_prev_timestamp:

		for cluster_curr in dict_traj_curr_timestamp:

			# If a trajectory did not go to any other cluster (next timestamp cluster), then it is a T_LEAVE relation.
			# If a trajectory did not come from any other cluster (prev timestamp cluster), then it is an T_ENTER relation.

			# Intersection of lists
			common_traj = [traj for traj in dict_traj_prev_timestamp[cluster_prev] if traj in dict_traj_curr_timestamp[cluster_curr]]

			if len(common_traj) > 0:
				# Eliminates trajectories we know went to a cluster (possibly the same id) in the next timestamp
				individual_traj_leave[cluster_prev] = np.setdiff1d(individual_traj_leave[cluster_prev], common_traj)
				# Eliminates trajectories we know came from a cluster (possibly the same id) in the previous timestamp
				individual_traj_enter[cluster_curr] = np.setdiff1d(individual_traj_enter[cluster_curr], common_traj)




	# IDENTIFIES SAME, C_ENTER, C_LEAVE
	# Use individual trajectories to calculate cross temporal cluster similarity and associate clusters

	# Note the 'cluster' at the dictionary name
	dict_cluster_prev_timestamp = {k: [] for k in cluster_list_prev}
	dict_cluster_curr_timestamp = {k: [] for k in cluster_list_curr}


	for cluster_prev in dict_traj_prev_timestamp:

		for cluster_curr in dict_traj_curr_timestamp:

			# Intersection of lists
			common_traj = [traj for traj in dict_traj_prev_timestamp[cluster_prev] if traj in dict_traj_curr_timestamp[cluster_curr]]

			# Associates cluster who share elements
			# Calculate cross temporal cluster similarity
			if len (common_traj) > 0:
				if is_same(dict_traj_prev_timestamp[cluster_prev], dict_traj_curr_timestamp[cluster_curr], individual_traj_leave[cluster_prev], individual_traj_enter[cluster_curr], common_traj):
					dict_cluster_prev_timestamp[cluster_prev].append([cluster_curr, SAME])
					dict_cluster_curr_timestamp[cluster_curr].append([cluster_prev, SAME])
				else:
					if len(common_traj) >= min_cluster:
						dict_cluster_prev_timestamp[cluster_prev].append([common_traj, cluster_curr, C_OUT])
						dict_cluster_curr_timestamp[cluster_curr].append([common_traj, cluster_prev, C_IN ])
					else:
						for traj in common_traj:
							dict_cluster_prev_timestamp[cluster_prev].append([traj, cluster_curr, T_LEAVE])
							dict_cluster_curr_timestamp[cluster_curr].append([traj, cluster_prev, T_ENTER])



	# IDENTIFY DISPERSE (0 SAME and 0  C_OUT)
	# IDENTIFY C_ENTER  (0 SAME and 1  C_OUT)
	# IDENTIFY SPLIT    (0 SAME and 2+ C_OUT)
	# IDENTIFY C_LEAVE  (1 SAME and conditions)
	for cluster_prev in dict_cluster_prev_timestamp:
		n_same = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == SAME])
		n_out  = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT])
		if n_same == 0:
			if n_out == 0:
				# DISPERSE
				temp = [traj[0] for traj in dict_cluster_prev_timestamp[cluster_prev] if traj[-1] == T_LEAVE]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != T_LEAVE]
				dict_cluster_prev_timestamp[cluster_prev].append([temp, DISPERSE])
			if n_out == 1:
				# C_ENTER
				temp = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev].append([temp[0], C_ENTER])
			if n_out >= 2:
				# SPLIT
				temp = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev].append([temp, SPLIT])
		if n_same == 1:
			if n_out >= 1:
				# C_LEAVE or C_OUT
				temp = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				f = lambda x: [cluster[-1] for cluster in x].count(True)
				has_same = [f(dict_cluster_curr_timestamp[t]) for t in temp]
				for i in range(len(temp)):
					if(has_same[i] == 0):
						#C_LEAVE
						dict_cluster_prev_timestamp[cluster_prev].append([temp[i], C_LEAVE])
					else:
						#C_OUT
						dict_cluster_prev_timestamp[cluster_prev].append([temp[i], C_OUT])
		if n_same >= 2:
			print("ERROR")



	# IDENTIFIES individual T_ENTER, T_LEAVE

	# Mark individual trajectories as ENTER OR LEAVE
	for cluster_prev in individual_traj_leave:
		dict_cluster_prev_timestamp[cluster_prev].extend([[traj, 0, T_LEAVE] for traj in individual_traj_leave[cluster_prev]])

	for cluster_curr in dict_traj_curr_timestamp:
		dict_cluster_curr_timestamp[cluster_curr].extend([[traj, 0, T_ENTER] for traj in individual_traj_enter[cluster_curr]])



	# IDENTIFY GROUP    (0 SAME and 0  C_IN)
	# IDENTIFY C_LEAVE  (0 SAME and 1  C_IN)
	# IDENTIFY MERGE    (0 SAME and 2+ C_IN)
	# IDENTIFY C_ENTER  (1 SAME and conditions)
	for cluster_curr in dict_cluster_curr_timestamp:
		n_same = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == SAME])
		n_in   = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN])
		if n_same == 0:
			if n_in  == 0:
				# GROUP
				temp = [traj[0] for traj in dict_cluster_curr_timestamp[cluster_curr] if traj[-1] == T_ENTER]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != T_ENTER]
				dict_cluster_curr_timestamp[cluster_curr].append([temp, GROUP])
			if n_in == 1:
				# C_LEAVE
				temp = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr].append([temp[0], C_LEAVE])
			if n_in >= 2:
				# MERGE
				temp = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr].append([temp, MERGE])
		if n_same == 1:
			if n_in >= 1:
				# C_ENTER or C_IN 
				temp = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				f = lambda x: [cluster[-1] for cluster in x].count(True)
				has_same = [f(dict_cluster_prev_timestamp[t]) for t in temp]
				for i in range(len(temp)):
					if(has_same[i] == 0):
						#C_ENTER
						dict_cluster_curr_timestamp[cluster_curr].append([temp[i], C_ENTER])
					else:
						#C_IN 
						dict_cluster_curr_timestamp[cluster_curr].append([temp[i], C_IN ])
		if n_same >= 2:
			print("ERROR")




	# IDENTIFY GROUP (No Same and 2+ T_ENTER)
	# IDENTIFY MERGE (No SAME and 2+ C_ENTER)
	#for cluster_curr in dict_cluster_curr_timestamp:
	#	n_same = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == SAME])
	#	n_in   = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN])
	#	if n_same > 0 and n_in  > 1:
	#		dict_cluster_curr_timestamp[cluster_curr] = [[cluster[0], MERGE] if cluster[-1] == C_ENTER else cluster for cluster in dict_cluster_curr_timestamp[cluster_curr]]






	# At this point, potential cluster or trajectory enters and leaves are marked.


	return dict_cluster_prev_timestamp, dict_cluster_curr_timestamp

	


def calc_cluster_id(clusters_prev_timestamp, clusters_curr_timestamp, dict_cluster_prev_timestamp, dict_cluster_curr_timestamp):


	dict_update_cluster = {} # internal id: universal id

	for cluster_curr in dict_cluster_curr_timestamp:
		exists_before = False
		for cluster_prev in dict_cluster_curr_timestamp[cluster_curr]:
			if cluster_prev[-1] == SAME:
				exists_before = True
				if cluster_curr != cluster_prev[0]:
					dict_update_cluster[cluster_curr] = cluster_prev[0]
				break
		if not exists_before:
			dict_update_cluster[cluster_curr] = constant.cluster_id_counter
			constant.cluster_id_counter += 1


	

	# Updates data structures with new universal cluster ids

	for internal_cluster_id in dict_update_cluster.keys():
		clusters_prev_timestamp['cid'][clusters_prev_timestamp['cid']==internal_cluster_id] = dict_update_cluster[internal_cluster_id]
		clusters_curr_timestamp['cid'][clusters_curr_timestamp['cid']==internal_cluster_id] = dict_update_cluster[internal_cluster_id]


	for internal_cluster_id in dict_cluster_prev_timestamp:
		# update values first
		for cluster_id in  dict_cluster_prev_timestamp[internal_cluster_id]:
			if type(cluster_id[0]) != list:
				if cluster_id[0] in dict_update_cluster.keys():
					cluster_id[0] = dict_update_cluster[cluster_id[0]]
			else:
					for c in cluster_id[0]:
						if c in dict_update_cluster.keys():
					 		c = dict_update_cluster[c]

		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_prev_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_prev_timestamp.pop(internal_cluster_id)


	for internal_cluster_id in dict_cluster_curr_timestamp:
		# update values first
		for cluster_id in dict_cluster_curr_timestamp[internal_cluster_id]:
			if type(cluster_id[0]) != list:
				if cluster_id[0] in dict_update_cluster.keys():
					cluster_id[0] = dict_update_cluster[cluster_id[0]]
			else:
				for c in cluster_id[0]:
					if c in dict_update_cluster.keys():
						c = dict_update_cluster[c]

		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_curr_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_curr_timestamp.pop(internal_cluster_id)






def save_relations(dict_cluster_prev_timestamp, dict_cluster_curr_timestamp, prev_timestamp, curr_timestamp):

	#new_clusters = {} # stores new clusters

	# Process Start relations
	#for cluster_curr in dict_cluster_curr_timestamp:
	#	if is_start(dict_cluster_curr_timestamp[cluster_curr]):
	#		new_cluster_id = constant.cluster_id_counter
	#		constant.cluster_id_counter += 1
	#		save_start(cluster_curr, new_cluster_id, curr_timestamp, dict_cluster_curr_timestamp[cluster_curr])
	#		new_clusters[cluster_curr] = new_cluster_id


	# Process Start relations (group or merge)
	for cluster_curr in dict_cluster_curr_timestamp:
		start = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == GROUP or cluster[-1] == MERGE]
		if(len(start) > 0):
			save_start(cluster_curr, curr_timestamp)

	


	# Process Leave / Split relations
	#for 

	# Process Enter / Merge
	#for

	# Process End relations
	#for



def save_start(id, timestamp):

	sid = str(id)
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	print 'save_start'
	print(sts + ' start ' + sid)
	# f = open(lifecycle_dir + str(new_id) + file_suffix, 'w')
	# s = ''
	# for cluster in clusters:
	# 	s += cluster + ', '
	# timestamp_str = datetime.strftime(timestamp, '%d %H:%M')
	# f.write(timestamp_str + ': ' + str(new_id) + ' ' + START_TXT + '(' + s + ').')


