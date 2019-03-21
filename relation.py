import constant
from constant import min_shared
from constant import min_cluster
from constant import lifecycle_dir
from constant import file_suffix
from constant import NO_CLUSTER
from file import save_relation

import numpy as np
from datetime import datetime

# relations
NO_RELATION = -1

SAME_P   = 00 # this is a prev node
SAME_C   = 01 # this is a curr node

START    = 10
END      = 11

T_ENTER  = 20
T_LEAVE  = 21

C_IN     = 30
C_OUT    = 31

JOIN     = 40
DETACH   = 41

C_ENTER  = 50
C_LEAVE  = 51

GROUP    = 60
DISPERSE = 61

MERGE    = 70
SPLIT    = 71





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
# def is_start(clusters):
# 	if all(c[-1] != SAME for c in clusters): return True
# 	else: return False


# def save_start(old_id, new_id, timestamp, clusters):
# 	f = open(lifecycle_dir + new_id + file_suffix, 'w')
# 	f.write(timestamp + ": " + new_id + " " + START_TXT)




def calc_relations(clusters_prev_timestamp, clusters_curr_timestamp):

	# Associates trajectories to clusters, and organize by cluster, on previous timestamp
	# Note the 'traj' at the dictionary name
	n_clusters_prev_timestamp = 0
	cluster_list_prev = []
	if len(clusters_prev_timestamp) > 0:
		cluster_list_prev = np.unique(clusters_prev_timestamp[:,-1:])
		cluster_list_prev = np.delete(cluster_list_prev, np.where(cluster_list_prev == NO_CLUSTER)) # removes (NO_CLUSTER)
		n_clusters_prev_timestamp = cluster_list_prev.size
	dict_traj_prev_timestamp = {k: [] for k in cluster_list_prev} 
	if n_clusters_prev_timestamp > 0: # accounts for the timestamp in which all trajectories do not belong to any cluster
		for traj in clusters_prev_timestamp:
			if traj[-1] != NO_CLUSTER:
				dict_traj_prev_timestamp[traj[-1]].append(traj[0]) # appends id to the entry of a specific cluster in the dictionary

	# Associates trajectories to clusters, and organize by cluster, on current timestamp
	# Note the 'traj' at the dictionary name
	n_clusters_curr_timestamp = 0
	cluster_list_curr = []
	if len(clusters_curr_timestamp) > 0:
		cluster_list_curr = np.unique(clusters_curr_timestamp[:,-1:])
		cluster_list_curr = np.delete(cluster_list_curr, np.where(cluster_list_curr == NO_CLUSTER)) # removes (NO_CLUSTER)
		n_clusters_curr_timestamp = cluster_list_curr.size
	dict_traj_curr_timestamp = {k: [] for k in cluster_list_curr} 
	if n_clusters_curr_timestamp > 0: # accounts for the timestamp in which all trajectories do not belong to any cluster
		for traj in clusters_curr_timestamp:
			if traj[-1] != NO_CLUSTER:
				dict_traj_curr_timestamp[traj[-1]].append(traj[0]) # appends id to the entry of a specific cluster in the dictionary



	# print('-----------------------')
	# print('dict_clusters_prev_timestamp')
	# print(dict_clusters_prev_timestamp)
	# print('dict_clusters_curr_timestamp')
	# print(dict_clusters_curr_timestamp)
	# print('-----------------------')




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
					dict_cluster_prev_timestamp[cluster_prev].append([cluster_curr, SAME_P])
					dict_cluster_curr_timestamp[cluster_curr].append([cluster_prev, SAME_C])
				else:
					if len(common_traj) >= min_cluster:
						dict_cluster_prev_timestamp[cluster_prev].append([common_traj, cluster_curr, C_OUT])
						dict_cluster_curr_timestamp[cluster_curr].append([common_traj, cluster_prev, C_IN ])
					else:
						for traj in common_traj:
							dict_cluster_prev_timestamp[cluster_prev].append([traj, cluster_curr, T_LEAVE])
							dict_cluster_curr_timestamp[cluster_curr].append([traj, cluster_prev, T_ENTER])




	# Helper function to discover whether a node has a SAME relationship or not
	f_p = lambda x: SAME_P in [cluster[-1] for cluster in x]
	f_c = lambda x: SAME_C in [cluster[-1] for cluster in x]




	# IDENTIFY DISPERSE (0 SAME and 0  C_OUT) (disperse can only be identified after individual trajectories have been added, so that T_LEAVES are updated correctly)
	# IDENTIFY JOIN     (0 SAME and 1  C_OUT)
	# IDENTIFY SPLIT    (0 SAME and 2+ C_OUT and some conditions)
	# IDENTIFY C_LEAVE  (1 SAME and conditions)
	for cluster_prev in dict_cluster_prev_timestamp:
		n_same = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == SAME_P])
		n_out  = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT])
		if n_same == 0:
			#if n_out == 0:
				# DISPERSE
				#temp = [traj[0] for traj in dict_cluster_prev_timestamp[cluster_prev] if traj[-1] == T_LEAVE]
				#dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != T_LEAVE]
				#dict_cluster_prev_timestamp[cluster_prev].append([temp, DISPERSE])
			if n_out == 1:
				# JOIN
				temp1 = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				temp2 = [cluster[1] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				dict_cluster_prev_timestamp[cluster_prev].append([temp1[0], temp2[0], JOIN])
			if n_out >= 2:
				# SPLIT
				temp1 = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				temp2 = [cluster[1] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				# has_same = [f(dict_cluster_curr_timestamp[t]) for t in temp2]
				# result = []
				# for i in range(len(temp)):
				# 	if(has_same[i] == 0):
				# 		# The current cluster started. Add its number.
				# 		result.append(temp2[i])
				# 	else:
				# 		# The current cluster existed before. Add its common trajectories.
				# 		result.append(temp[i])
				# dict_cluster_prev_timestamp[cluster_prev].append([result, SPLIT])
				# 
				# 
				# Another solution
				# temp = []
				# for i in len(temp1):
				# 	temp.append([temp1[i], temp2[i]])
				for i in range(len(temp1)):
					dict_cluster_prev_timestamp[cluster_prev].append([temp1[i], temp2[i], SPLIT])
		if n_same == 1:
			if n_out >= 1:
				# C_LEAVE or C_OUT
				temp1 = [cluster[0] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				temp2 = [cluster[1] for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != C_OUT]
				has_same = [f_c(dict_cluster_curr_timestamp[t]) if t != 0 else False for t in temp2]
				for i in range(len(temp1)):
					if(has_same[i] == 0):
						#C_LEAVE
						dict_cluster_prev_timestamp[cluster_prev].append([temp1[i], temp2[i], C_LEAVE])
					else:
						#C_OUT 
						dict_cluster_prev_timestamp[cluster_prev].append([temp1[i], temp2[i], C_OUT])
		if n_same >= 2:
			assert(0)





	# IDENTIFIES individual T_ENTER, T_LEAVE

	# Mark individual trajectories as ENTER OR LEAVE
	for cluster_prev in individual_traj_leave:
		dict_cluster_prev_timestamp[cluster_prev].extend([[traj, NO_CLUSTER, T_LEAVE] for traj in individual_traj_leave[cluster_prev]])

	for cluster_curr in dict_traj_curr_timestamp:
		dict_cluster_curr_timestamp[cluster_curr].extend([[traj, NO_CLUSTER, T_ENTER] for traj in individual_traj_enter[cluster_curr]])


	# IDENTIFY DISPERSE
	for cluster_prev in dict_cluster_prev_timestamp:
		n_same   = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == SAME_P])
		n_out    = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT])
		n_split  = len([1 for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == SPLIT])
		if n_same == 0 and n_out == 0 and n_split == 0:
			# DISPERSE
			temp = [traj[0] for traj in dict_cluster_prev_timestamp[cluster_prev] if traj[-1] == T_LEAVE]
			if len(temp) > 0:
				dict_cluster_prev_timestamp[cluster_prev] = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] != T_LEAVE]
				dict_cluster_prev_timestamp[cluster_prev].append([temp, DISPERSE])





	# IDENTIFY GROUP    (0 SAME and 0  C_IN)
	# IDENTIFY DETACH   (0 SAME and 1  C_IN)
	# IDENTIFY MERGE    (0 SAME and 2+ C_IN and some conditions)
	# IDENTIFY C_ENTER  (1 SAME and conditions)
	for cluster_curr in dict_cluster_curr_timestamp:
		n_same = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == SAME_C])
		n_in   = len([1 for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN])
		if n_same == 0:
			if n_in  == 0:
				# GROUP
				temp = [traj[0] for traj in dict_cluster_curr_timestamp[cluster_curr] if traj[-1] == T_ENTER]
				if len(temp) > 0:
					dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != T_ENTER]
					dict_cluster_curr_timestamp[cluster_curr].append([temp, GROUP])
			if n_in == 1:
				# DETACH
				# temp = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				# dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				# dict_cluster_curr_timestamp[cluster_curr].append([temp[0], C_LEAVE])

				temp1 = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				temp2 = [cluster[1] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				dict_cluster_curr_timestamp[cluster_curr].append([temp1[0], temp2[0], DETACH])
			if n_in >= 2:
				# MERGE
				temp1 = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				temp2 = [cluster[1] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				# has_same = [f(dict_cluster_prev_timestamp[t]) for t in temp2]
				# result = []
				# for i in range(len(temp)):
				# 	if(has_same[i] == 0):
				# 		# The previous cluster ended. Add its number.
				# 		result.append(temp2[i])
				# 	else:
				# 		# The previous cluster continues to exist. Add its common trajectories.
				# 		result.append(temp[i])
				# dict_cluster_curr_timestamp[cluster_curr].append([result, MERGE])

				for i in range(len(temp1)):
					dict_cluster_curr_timestamp[cluster_curr].append([temp1[i], temp2[i], MERGE])

		if n_same == 1:
			if n_in >= 1:
				# C_ENTER or C_IN
				temp1 = [cluster[0] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				temp2 = [cluster[1] for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
				dict_cluster_curr_timestamp[cluster_curr] = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] != C_IN]
				has_same = [f_p(dict_cluster_prev_timestamp[t]) if t != 0 else False for t in temp2]
				for i in range(len(temp1)):
					if(has_same[i] == 0):
						#C_ENTER
						dict_cluster_curr_timestamp[cluster_curr].append([temp1[i], temp2[i], C_ENTER])
					else:
						#C_IN 
						dict_cluster_curr_timestamp[cluster_curr].append([temp1[i], temp2[i], C_IN])
		if n_same >= 2:
			assert(0)






	# At this point, potential cluster or trajectory enters and leaves are marked.


	return dict_cluster_prev_timestamp, dict_cluster_curr_timestamp

	


def calc_cluster_id(clusters_prev_timestamp, clusters_curr_timestamp, dict_cluster_prev_timestamp, dict_cluster_curr_timestamp):


	dict_update_cluster = {} # internal id: universal id

	for cluster_curr in dict_cluster_curr_timestamp:
		exists_before = False
		for cluster_prev in dict_cluster_curr_timestamp[cluster_curr]:
			if cluster_prev[-1] == SAME_C:
				exists_before = True
				if cluster_curr != cluster_prev[0]:
					dict_update_cluster[cluster_curr] = cluster_prev[0]
				break
		if not exists_before:
			dict_update_cluster[cluster_curr] = constant.cluster_id_counter
			constant.cluster_id_counter += 1


	

	# Updates data structures with new universal cluster ids

	for internal_cluster_id in dict_update_cluster.keys():
		if clusters_prev_timestamp.size != 0: clusters_prev_timestamp[:,-1:][clusters_prev_timestamp[:,-1:]==internal_cluster_id] = dict_update_cluster[internal_cluster_id]
		if clusters_curr_timestamp.size != 0: clusters_curr_timestamp[:,-1:][clusters_curr_timestamp[:,-1:]==internal_cluster_id] = dict_update_cluster[internal_cluster_id]


	for internal_cluster_id in dict_cluster_prev_timestamp.keys():
		# update values first
		for cluster_id in dict_cluster_prev_timestamp[internal_cluster_id]:
			if cluster_id[1] in dict_update_cluster.keys():
				cluster_id[1] = dict_update_cluster[cluster_id[1]]

		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_prev_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_prev_timestamp.pop(internal_cluster_id)


	for internal_cluster_id in dict_cluster_curr_timestamp.keys():
		# update values first
		for cluster_id in dict_cluster_curr_timestamp[internal_cluster_id]:
			if cluster_id[1] in dict_update_cluster.keys():
				cluster_id[1] = dict_update_cluster[cluster_id[1]]

		# update keys later
		if internal_cluster_id in dict_update_cluster.keys():
			dict_cluster_curr_timestamp[dict_update_cluster[internal_cluster_id]] = dict_cluster_curr_timestamp.pop(internal_cluster_id)






def save_relations(dict_cluster_prev_timestamp, dict_cluster_curr_timestamp, prev_timestamp, curr_timestamp):


	# Process START relations (group or merge)
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == GROUP or cluster[-1] == MERGE or cluster[-1] == DETACH]
		if(len(relation) > 0):
			save_start(cluster_curr, curr_timestamp)

	# Process MERGE relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == MERGE]
		for r in relation:
			save_merge(cluster_curr, curr_timestamp, r[0], r[1])

	# Process GROUP relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == GROUP]
		if(len(relation) > 0):
			save_group(cluster_curr, curr_timestamp, relation[0][0])

	# Process DETACH relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == DETACH]
		for r in relation:
			save_detach(cluster_curr, curr_timestamp, r[0], r[1])




	# Process T_LEAVE relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == T_LEAVE]
		for r in relation:
			save_t_leave(cluster_prev, prev_timestamp, r[0], r[1])

	# Process C_LEAVE relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_LEAVE]
		for r in relation:
			save_c_leave(cluster_prev, prev_timestamp, r[0], r[1])

	# Process C_OUT relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == C_OUT]
		for r in relation:
			save_c_out(cluster_prev, prev_timestamp, r[0], r[1])




	# Process C_IN relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_IN]
		for r in relation:
			save_c_in(cluster_curr, curr_timestamp, r[0], r[1])

	# Process C_ENTER relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == C_ENTER]
		for r in relation:
			save_c_enter(cluster_curr, curr_timestamp, r[0], r[1])

	# Process T_ENTER relations
	for cluster_curr in dict_cluster_curr_timestamp:
		relation = [cluster for cluster in dict_cluster_curr_timestamp[cluster_curr] if cluster[-1] == T_ENTER]
		for r in relation:
			save_t_enter(cluster_curr, curr_timestamp, r[0], r[1])




	# Process JOIN relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == JOIN]
		for r in relation:
			save_join(cluster_prev, prev_timestamp, r[0], r[1])

	# Process DISPERSE relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == DISPERSE]
		if(len(relation) > 0):
			save_disperse(cluster_prev, prev_timestamp, relation[0][0])

	# Process SPLIT relations
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == SPLIT]
		for r in relation:
			save_split(cluster_prev, prev_timestamp, r[0], r[1])

	# Process END relations (group or merge)
	for cluster_prev in dict_cluster_prev_timestamp:
		relation = [cluster for cluster in dict_cluster_prev_timestamp[cluster_prev] if cluster[-1] == DISPERSE or cluster[-1] == SPLIT or cluster[-1] == JOIN]
		if(len(relation) > 0):
			save_end(cluster_prev, prev_timestamp)


def save_start(id, timestamp):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' start(' + sid + ')'

	save_relation(path, s)


def save_merge(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	# c = ''
	# for cluster in clusters:
	# 	if type(cluster) != list:
	# 		c += str(int(cluster)) + ', '
	# 	else:
	# 		c += str([int(i) for i in cluster]) + ', '
	# c = c[:-2] # removes last ', '

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' merge(' + t + ', ' + c + ', ' + sid + ')'

	save_relation(path, s)


def save_group(id, timestamp, trajs):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	# t = ''
	# for traj in trajs:
	# 	t += str(int(traj)) + ', '
	t = str([int(traj) for traj in trajs])
	# t = t[:-2] # removes last ', '

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' group(' + t + ', ' + sid + ')'

	save_relation(path, s)


def save_detach(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' detach(' + t + ', ' + c + ', ' + sid + ')' 

	save_relation(path, s)


def save_t_leave(id, timestamp, traj, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str(int(traj))
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' t_leave(' + t + ', ' + c + ', ' + sid +')'

	save_relation(path, s)


def save_c_leave(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' c_leave(' + t + ', ' + c + ', ' + sid + ')' 

	save_relation(path, s)


def save_c_out(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	# t = ''
	# for traj in trajs:
	# 	t += str(int(traj)) + ', '
	t = str([int(traj) for traj in trajs])
	# t = t[:-2] # removes last ', '

	c = str(int(cluster))

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' c_out(' + t + ', ' + c + ', ' + sid + ')'

	save_relation(path, s)


def save_c_in(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	# t = ''
	# for traj in trajs:
	# 	t += str(int(traj)) + ', '
	# t = t[:-2] # removes last ', '

	c = str(int(cluster))

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' c_in(' + t + ', ' + c + ', ' + sid + ')'

	save_relation(path, s)


def save_c_enter(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' c_enter(' + t + ', ' + c + ', ' + sid + ')' 

	save_relation(path, s)


def save_t_enter(id, timestamp, traj, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str(int(traj))
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' t_enter(' + t + ', ' + c + ', ' + sid +')'

	save_relation(path, s)


def save_join(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	path = lifecycle_dir + sid + file_suffix
	s = sts + ' join(' + t + ', ' + c + ', ' + sid + ')' 

	save_relation(path, s)


def save_disperse(id, timestamp, trajs):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	t = str([int(traj) for traj in trajs])
	# t = ''
	# for traj in trajs:
	# 	t += str(int(traj)) + ', '
	# t = t[:-2] # removes last ', '

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' disperse(' + t + ', ' + sid + ')'

	save_relation(path, s)


def save_split(id, timestamp, trajs, cluster):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')


	t = str([int(traj) for traj in trajs])
	c = str(int(cluster))
	# c = str([int(cluster) if type(cluster) != list else [int(i) for i in cluster] for cluster in clusters])
	# c = ''
	# for cluster in clusters:
	# 	if type(cluster) != list:
	# 		c += str(int(cluster)) + ', '
	# 	else:
	# 		c += str([int(i) for i in cluster]) + ', '
	# c = c[:-2] # removes last ', '

	path = lifecycle_dir + sid + file_suffix
	# s = sts + ' split(' + c + ', ' + sid + ')'
	s = sts + ' split(' + t + ', ' + c + ', ' + sid + ')'

	save_relation(path, s)


def save_end(id, timestamp):

	sid = str(int(id))
	sts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

	path = lifecycle_dir + sid + file_suffix
	s = sts + ' end(' + sid + ')'

	save_relation(path, s)