from datetime import datetime
from datetime import timedelta
from constant import cluster_dir
from constant import preprocessed2_dir
from constant import preprocessedneo4j_dir
from constant import nodes_filename
from constant import edges_filename
from constant import rate
from constant import NODES_HEADER
from constant import EDGES_HEADER
from file     import identify_clusters

import time
import ciso8601

import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

from sklearn.cluster import DBSCAN

from relation import START
from relation import END
from relation import T_ENTER
from relation import T_LEAVE
from relation import C_IN
from relation import C_OUT
from relation import JOIN
from relation import DETACH
from relation import C_ENTER
from relation import C_LEAVE
from relation import GROUP
from relation import DISPERSE
from relation import MERGE
from relation import SPLIT

from relation import relation_to_string
from relation import string_to_relation

# Prepare to import to Neo4j

def preprocess_neo4j():

	f_nodes   = open(preprocessedneo4j_dir + nodes_filename, 'w')
	f_edges   = open(preprocessedneo4j_dir + edges_filename, 'w')

	f_nodes.write(NODES_HEADER) # header
	f_edges.write(EDGES_HEADER) # header


	clusters = identify_clusters(cluster_dir)

	for cluster in clusters:

		f_cluster = open(cluster_dir + cluster, 'r')
		cluster_id = parse_cluster_id(cluster)

		# helps identify relationships where nothing has happened (relationship SAME or CONTINUE)
		# helps identify relationships that happen at the same time a start or end relationship
		time_start = parse_timestamp(f_cluster.readline())
		for line in f_cluster: pass
		time_end   = parse_timestamp(line)
		timeline = time_start

		f_cluster.seek(0)

		flag_start = False # used to identify events happening at the start time
		flag_end   = False # used to identify events happening at the end time

		for line in f_cluster:
			timestamp = parse_timestamp(line)
			event = parse_event(line)
			if (timestamp == time_start):
				if (event == T_ENTER or event == C_ENTER or event == C_IN ): flag_start = True;
			if (timestamp == time_end):
				if (event == T_LEAVE or event == C_LEAVE or event == C_OUT): flag_end   = True;

		f_cluster.seek(0)

		size = 0
		participants = []

		event_cache = ''	 # used to identify many events at the same time
		timestamp_cache = '' # used to identify many events at the same time

		for line in f_cluster:

			timestamp              = parse_timestamp(line)
			latitude               = parse_latitude(line)
			longitude              = parse_longitude(line)
			event                  = parse_event(line)
			contribution           = parse_size(event, line)
			size                   = size + contribution
			participants_event     = parse_participants_event(event, line)
			supporting_cluster_id  = parse_supporting_cluster_id(event, line)


			nodes = parse_nodes(cluster_id, event, event_cache, timestamp, timestamp_cache, latitude, longitude, size-contribution, size, participants, participants_event, time_start, time_end, flag_start, flag_end)
			edges = parse_edges(cluster_id, supporting_cluster_id, timestamp, event, participants_event, time_start, time_end, flag_start, flag_end)

			write_nodes(nodes, f_nodes)
			write_edges(edges, f_edges)

			continues = parse_continues(cluster_id, timestamp, timeline, event, time_start, time_end)
			write_continues(continues, f_edges)

			size = update_size(size, contribution, event)
			participants = update_participants(participants, participants_event, event)
			timeline = update_timeline(timestamp, event, time_start, time_end, flag_start, flag_end)
			event_cache = event
			timestamp_cache = timestamp


		f_cluster.close()
	f_nodes.close()
	f_edges.close()



# Identify the cluster information
def parse_cluster_id(filename): return filename[0:-4]
def parse_timestamp(line):      return datetime.strptime(line[0:19], '%Y-%m-%d %H:%M:%S')
def parse_latitude(line):       return line[20:30]
def parse_longitude(line):      return line[31:41]
def parse_event(line):          return string_to_relation(line[42:line.index('(')])



# Identifies the size of the cluster after the event

def parse_size(event, line):

	# all other events include squared brackets, thus their parsing can be summarized in one line of code

	if (event == START): return  0
	if (event == END  ): return  0

	if (event == T_ENTER): return  1
	if (event == T_LEAVE): return -1

	if (event == C_IN
	or  event == DETACH
	or  event == C_ENTER
	or  event == GROUP
	or  event == MERGE): return   line.count(',', line.index('['), line.index(']')) + 1

	if (event == C_OUT
	or  event == JOIN
	or  event == C_LEAVE
	or  event == DISPERSE
	or  event == SPLIT): return - (line.count(',', line.index('['), line.index(']')) + 1)


# Identifies the participants of a cluster event

def parse_participants_event(event, line):

	if (event == START): return []
	if (event == END)  : return []

	if (event == T_ENTER
	or  event == T_LEAVE): return [line[line.index('(')+1: line.index(')')].split(', ')[0]]

	if (event == C_IN
	or  event == DETACH
	or  event == C_ENTER
	or  event == GROUP
	or  event == MERGE
	or  event == C_OUT
	or  event == JOIN
	or  event == C_LEAVE
	or  event == DISPERSE
	or  event == SPLIT): return line[line.index('[')+1:line.index(']')].split(', ')


# Identifies the destination of the relationship

def parse_supporting_cluster_id(event, line):

	if (event == START): return ''
	if (event == END)  : return ''

	if (event == GROUP)   : return ''
	if (event == DISPERSE): return ''

	if (event == T_ENTER): return ''
	if (event == T_LEAVE): return ''

	if (event == C_IN
	or  event == JOIN
	or  event == C_ENTER
	or  event == MERGE): return line.split(',')[-2][1:] # supporting cluster_id

	if (event == C_OUT
	or  event == DETACH
	or  event == C_LEAVE
	or  event == SPLIT): return line.split(',')[-2][1:] # supporting cluster_id


# Prepares a list of CVS entries for nodes

def parse_nodes(nodeId, event, event_cache, timestamp, timestamp_cache, latitude, longitude, nodeSizeBefore, nodeSizeAfter, participants, participants_event, time_start, time_end, flag_start, flag_end):

	if (event == START):    return []
	if (event == END)  :    return []

	if event_cache == T_LEAVE or event_cache == C_LEAVE: timestamp_cache = timestamp_cache + timedelta(minutes=rate)

	if (event == GROUP)   : return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter , participants_event)]
	if (event == DISPERSE):
		if (time_start == time_end and (flag_start or flag_end)):
			return []
		else:
			return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants_event)]

	if (event == T_ENTER
	or  event == C_ENTER
	or  event == C_IN):
		if (time_start == time_end):
			return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, participants + participants_event)]
		elif (timestamp == time_start):
			if (timestamp != timestamp_cache):
				return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, (timestamp + timedelta(minutes=rate)/2), latitude, longitude, nodeSizeAfter, participants+participants_event)]
			else:
				return [parse_node(nodeId, (timestamp + timedelta(minutes=rate)/2), latitude, longitude, nodeSizeAfter, participants+participants_event)]
		elif (timestamp == time_end and flag_end):
			if (timestamp != timestamp_cache):
				return [parse_node(nodeId, (timestamp - timedelta(minutes=rate)), latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, (timestamp - timedelta(minutes=rate)/2), latitude, longitude, nodeSizeAfter, participants+participants_event)]
			else:
				return [parse_node(nodeId, (timestamp - timedelta(minutes=rate)/2), latitude, longitude, nodeSizeAfter, participants+participants_event)]
		else:
			if (timestamp != timestamp_cache):
				return [parse_node(nodeId, (timestamp - timedelta(minutes=rate)), latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, participants+participants_event)]
			else:
				return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, participants+participants_event)]
			

	if (event == T_LEAVE
	or  event == C_LEAVE
	or  event == C_OUT):
		if (time_start == time_end):
			return [] # return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants)]
		elif (timestamp == time_end):
			if (timestamp != timestamp_cache - timedelta(minutes=rate)):
				return [parse_node(nodeId, (timestamp - timedelta(minutes=rate)/2), latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
			else:
				return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
		elif (timestamp == time_start and flag_start):
			if (timestamp != timestamp_cache - timedelta(minutes=rate)):
				return [parse_node(nodeId, (timestamp + timedelta(minutes=rate)/2), latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, (timestamp + timedelta(minutes=rate)), latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
			else:
				return [parse_node(nodeId, (timestamp + timedelta(minutes=rate)), latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
		else:
			if (timestamp != timestamp_cache - timedelta(minutes=rate)):
				return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants), parse_node(nodeId, (timestamp + timedelta(minutes=rate)), latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
			else:
				return [parse_node(nodeId, (timestamp + timedelta(minutes=rate)), latitude, longitude, nodeSizeAfter, [p for p in participants if p not in participants_event])]
			



	if (event == JOIN):
		if(time_start == time_end and (flag_start or flag_end)):
			return []
		else:
		    return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants_event)]
	if (event == DETACH):   return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter , participants_event)]

	
	if  (event == MERGE and event_cache != MERGE): return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeAfter, participants+participants_event)]
	elif(event == MERGE and event_cache == MERGE): return []
	if  (event == SPLIT and event_cache != SPLIT): return [parse_node(nodeId, timestamp, latitude, longitude, nodeSizeBefore, participants)]
	elif(event == SPLIT and event_cache == SPLIT): return []




# Prepares a list of CSV entries for edges

def parse_edges(nodeId, supportingNodeId, timestamp, event, participants_event, time_start, time_end, flag_start, flag_end):

	if (event == START):    return []
	if (event == END)  :    return []

	if (event == GROUP)   : return []
	if (event == DISPERSE): return []

	if (event == T_ENTER):
		if(time_start == time_end):
			return [parse_edge(nodeId, nodeId, timestamp, timestamp, relation_to_string(event), participants_event)]
		elif (timestamp == time_start + timedelta(minutes=rate) and flag_start):
			return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)/2), timestamp, relation_to_string(event), participants_event)]
		elif (timestamp == time_start):
			return [parse_edge(nodeId, nodeId, timestamp, (timestamp + timedelta(minutes=rate)/2), relation_to_string(event), participants_event)]
		elif (timestamp == time_end and flag_end):
			return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)), (timestamp - timedelta(minutes=rate)/2), relation_to_string(event), participants_event)]
		else:
			return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event), participants_event)]
	if (event == T_LEAVE):
		if(time_start == time_end):
			return [parse_edge(nodeId, nodeId, timestamp, timestamp, relation_to_string(event), participants_event)]
		elif (timestamp == time_end - timedelta(minutes=rate) and flag_end):
			return [parse_edge(nodeId, nodeId, timestamp, (timestamp + timedelta(minutes=rate)/2), relation_to_string(event), participants_event)]
		elif (timestamp == time_end):
			return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)/2), timestamp, relation_to_string(event), participants_event)]
		elif (timestamp == time_start and flag_start):
			return [parse_edge(nodeId, nodeId, (timestamp + timedelta(minutes=rate)/2), (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]
		else:
			return [parse_edge(nodeId, nodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]

	if (event == C_LEAVE):
		edges = [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]
		if(time_start == time_end):
			return edges + [parse_continue(nodeId, timestamp, timestamp)]
		elif (timestamp == time_end - timedelta(minutes=rate) and flag_end):
			return edges + [parse_continue(nodeId, timestamp, (timestamp + timedelta(minutes=rate)/2))]
		elif (timestamp == time_end):
			return edges + [parse_continue(nodeId, (timestamp - timedelta(minutes=rate)/2), timestamp)]
		elif (timestamp == time_start and flag_start):
			return edges + [parse_continue(nodeId, (timestamp + timedelta(minutes=rate)/2), (timestamp + timedelta(minutes=rate)))]
		else:
			return edges + [parse_continue(nodeId, timestamp, (timestamp + timedelta(minutes=rate)))]
	if (event == C_OUT  ): return [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]

	if (event == C_ENTER):
		edges = [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event), participants_event)]
		if(time_start == time_end):
			return edges + [parse_continue(nodeId, timestamp, timestamp)]
		elif (timestamp == time_start + timedelta(minutes=rate) and flag_start):
			return edges + [parse_continue(nodeId, (timestamp - timedelta(minutes=rate)/2), timestamp)]
		elif (timestamp == time_start):
			return edges + [parse_continue(nodeId, timestamp, (timestamp + timedelta(minutes=rate)/2))]
		elif (timestamp == time_end and flag_end):
			return edges + [parse_continue(nodeId, (timestamp - timedelta(minutes=rate)), (timestamp - timedelta(minutes=rate)/2))]
		else:
			return edges + [parse_continue(nodeId, (timestamp - timedelta(minutes=rate)), timestamp)]
	if (event == C_IN   ): return [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event), participants_event)]

	if (event == JOIN):    return [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]
	if (event == DETACH):  return [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event), participants_event)]
	
	if (event == MERGE):   return [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event), participants_event)]
	if (event == SPLIT):   return [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event), participants_event)]


def parse_continues(cluster_id, timestamp, timeline, event, time_start, time_end):

	if timeline == '': return []

	if (event == START): return  []
	if (event == END  ): return  []

	if (event == T_ENTER
	or 	event == C_IN
	or  event == DETACH
	or  event == C_ENTER
	or  event == GROUP
	or  event == MERGE):
		if (timestamp > timeline + timedelta(minutes=rate)): return [parse_continue(cluster_id, timeline, timestamp - timedelta(minutes=rate))]

	if (event == T_LEAVE
	or 	event == C_OUT
	or  event == C_LEAVE):
		if (timestamp > timeline):
			if (timestamp != time_end): return [parse_continue(cluster_id, timeline, timestamp)]
			else: return [parse_continue(cluster_id, timeline, (timestamp - timedelta(minutes=rate)/2))]

	if (event == JOIN
	or  event == DISPERSE
	or  event == SPLIT):
		if (timestamp > timeline):
			return [parse_continue(cluster_id, timeline, timestamp)]

	return []





# Creates the CSV entry for a node
def parse_node(nodeId, timestamp, latitude, longitude, nodeSize, participants):
	return nodeId + ',' + timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + latitude + ',' + longitude + ',' + str(nodeSize) + ',' + '"' + ','.join(participants) + '"' + '\n'

# Creates the CSV entry for an edge
def parse_edge(nodeId, supportingNodeId, timestamp_start, timestamp_end, edgeName, participants):
	return nodeId + ',' + supportingNodeId + ',' + timestamp_start.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + timestamp_end.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + edgeName + ',' + '"' + ','.join(participants) + '"' + '\n'

# Creates the CSV entry for an continue
def parse_continue(nodeId, timestamp_start, timestamp_end):
	return parse_edge(nodeId, nodeId, timestamp_start, timestamp_end, 'CONTINUE', [])


# Writes each node in the CSV file
def write_nodes(nodes, f_nodes):
	for node in nodes: f_nodes.write(node);

# Writes each edge in the CSV file
def write_edges(edges, f_edges):
	for edge in edges: f_edges.write(edge);

# Writes each continue in the CSV file
def write_continues(continues, f_edges):
	write_edges(continues, f_edges)



def update_timeline(timestamp, event, time_start, time_end, flag_start, flag_end):

	if (event == START)   : return timestamp
	if (event == END)     : return timestamp

	if (event == GROUP)   : return timestamp
	if (event == DISPERSE): return timestamp + timedelta(minutes=rate)

	if (event == T_ENTER):
		if(time_start == time_end): return timestamp
		elif (timestamp == time_start + timedelta(minutes=rate) and flag_start): return timestamp
		elif (timestamp == time_start): return timestamp + timedelta(minutes=rate)/2
		elif (timestamp == time_end and flag_end): return timestamp - timedelta(minutes=rate)/2
		else: return timestamp

	if (event == T_LEAVE):
		if(time_start == time_end): return timestamp
		elif (timestamp == time_end - timedelta(minutes=rate) and flag_end): return timestamp + timedelta(minutes=rate)/2
		elif (timestamp == time_end): return timestamp
		elif (timestamp == time_start and flag_start): return timestamp + timedelta(minutes=rate)
		else: return timestamp + timedelta(minutes=rate)

	if (event == C_ENTER):
		if(time_start == time_end): return timestamp
		elif (timestamp == time_start + timedelta(minutes=rate) and flag_start): return timestamp
		elif (timestamp == time_start): return timestamp + timedelta(minutes=rate)/2
		elif (timestamp == time_end and flag_end): return timestamp - timedelta(minutes=rate)/2
		else: return timestamp

	if (event == C_LEAVE):
		if(time_start == time_end): return timestamp
		elif (timestamp == time_end - timedelta(minutes=rate) and flag_end): return timestamp + timedelta(minutes=rate)/2
		elif (timestamp == time_end): return timestamp
		elif (timestamp == time_start and flag_start): return timestamp + timedelta(minutes=rate)
		else: return timestamp + timedelta(minutes=rate)

	# if (event == T_ENTER
	# or  event == C_ENTER
	# or  event == C_IN):
	# 	if (timestamp != time_start):  return timestamp
	# 	else: return (timestamp + timedelta(minutes=rate)/2)

	# if (event == T_LEAVE
	# or  event == C_LEAVE
	# or  event == C_OUT):
	# 	if (timestamp != time_end):  return timestamp + timedelta(minutes=rate)
	# 	else: return timestamp

	if (event == C_IN):     return timestamp
	if (event == C_OUT):    return timestamp + timedelta(minutes=rate)

	if (event == JOIN)  :   return timestamp + timedelta(minutes=rate)
	if (event == DETACH):   return timestamp
	
	if (event == MERGE):    return timestamp
	if (event == SPLIT):    return timestamp + timedelta(minutes=rate)



def update_size(size, contribution, event):
	if  event == SPLIT: return size - contribution
	return size


def update_participants(participants, participants_event, event):

	if (event == START): return participants
	if (event == END)  : return participants

	if (event == GROUP
	or  event == T_ENTER
	or  event == DETACH
	or  event == C_ENTER
	or  event == C_IN
	or  event == MERGE): return participants + participants_event

	if (event == DISPERSE
	or  event == T_LEAVE
	or  event == JOIN
	or  event == C_LEAVE
	or  event == C_OUT
	or  event == SPLIT): return [p for p in participants if p not in participants_event]
