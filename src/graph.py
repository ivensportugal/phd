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

		# helps identify relations where nothing has happened (relation SAME or CONTINUE)
		timeline = ''
		for line in f_cluster:
			timeline = parse_timestamp(line)
			break
		f_cluster.seek(0)

		size = 0

		event_cache = ''	 # used to identify many events at the same time
		timestamp_cache = '' # used to identify many events at the same time

		for line in f_cluster:

			timestamp              = parse_timestamp(line)
			event                  = parse_event(line)
			contribution           = parse_size(event, line)
			size                   = size + contribution
			supporting_cluster_id  = parse_supporting_cluster_id(event, line)

			nodes = parse_nodes(cluster_id, size-contribution, size, timestamp, event, event_cache, timestamp_cache)
			edges = parse_edges(cluster_id, supporting_cluster_id, timestamp, event)

			write_nodes(nodes, f_nodes)
			write_edges(edges, f_edges)

			continues = parse_continues(cluster_id, timestamp, timeline, event)
			write_continues(continues, f_edges)

			timeline = update_timeline(timestamp, event)
			event_cache = event
			timestamp_cache = timestamp


		f_cluster.close()
	f_nodes.close()
	f_edges.close()





# # Perpare to import to Neo4j

# def preprocess_neo4j():

# 	clusters = identify_clusters(cluster_dir)
# 	identify_nodes(clusters)
# 	identify_edges(clusters)


# def identify_nodes(clusters):

# 	for cluster in clusters:

# 		f_cluster = open(cluster_dir + cluster,   'r')
# 		f_nodes   = open(preprocessedneo4j_dir + nodes_filename, 'w')

# 		cluster_id   = parse_cluster_id(cluster)
# 		cluster_size = 0

# 		cached_timestamp              = ''
# 		cached_event                  = ''
# 		cached_cluster_event          = ''
# 		cached_cluster_size           = ''
# 		cached_cluster_id_destination = ''

# 		for line in f_cluster:
			
# 			timestamp              = parse_timestamp(line)
# 			event, cluster_event   = parse_event(line)
# 			cluster_size  		   = cluster_size + parse_size(cluster_event, line)
# 			cluster_id_destination = parse_destination(cluster_event, line)

# 			if cluster_event == START: continue
# 			if cluster_event == END  : 
# 				node = parse_node(cluster_id, cluster_size, timestamp)
# 				f_nodes.write(node)
# 				continue


# 			if cached_event == '':
# 				cached_timestamp     		  = timestamp
# 				cached_event         		  = event
# 				cached_cluster_event 		  = cluster_event
# 				cached_cluster_size  		  = cluster_size
# 				cached_cluster_id_destination = cluster_id_destination
# 				continue

# 			else:
# 				if cached_cluster_event == cluster_event and cached_timestamp == timestamp:
# 						cached_cluster_size = cached_cluster_size + cluster_size
# 						continue
# 				else:
# 					temp_timestamp 					= cached_timestamp
# 					temp_event 						= cached_event
# 					temp_cluster_event 				= cached_cluster_event
# 					temp_cluster_size 				= cached_cluster_size
# 					temp_cluster_id_destination 	= cached_cluster_id_destination

# 					cached_timestamp				= timestamp
# 					cached_event					= event
# 					cached_cluster_event			= cluster_event
# 					cached_cluster_size				= cluster_size
# 					cached_cluster_id_destination	= cluster_id_destination

# 					timestamp 						= temp_timestamp
# 					event 							= temp_event
# 					cluster_event 					= temp_cluster_event
# 					cluster_size 					= temp_cluster_size
# 					cluster_id_destination 			= temp_cluster_id_destination


# 			node = parse_node(cluster_id, cluster_size, timestamp)
# 			f_nodes.write(node)



# 		f_cluster.close()
# 		f_nodes.close()
# 		f_edges.close()

# 			# if event == START   : continue
# 			# if event == END     : continue

# 			# if event == T_ENTER : cache (increase size) (time shown in curr)
# 			# if event == T_LEAVE : cache (decrease size) (time shown in prev)

# 			# if event == C_IN    : process (wont find it)
# 			# if event == C_OUT   : process (wont find it)

# 			# if event == JOIN    : process time shown in prev - final
# 			# if event == DETACH  : process time shown in curr - initial

# 			# if event == C_ENTER : cache (increase size) (time shown in curr)
# 			# if event == C_LEAVE : cache (decrease size) (time shown in prev)

# 			# if event == GROUP   : process time shown is curr - initial
# 			# if event == DISPERSE: process time shown is prev - final

# 			# if event == MERGE   : cache time shown is curr - initial
# 			# if event == SPLIT   : cache time shown is prev - final



# def identify_edges(clusters):

# 	for cluster in clusters:



# 		f_cluster = open(cluster_dir + cluster,   'r')
# 		f_nodes   = open(preprocessedneo4j_dir + nodes_filename, 'w')
# 		f_edges   = open(preprocessedneo4j_dir + edges_filename, 'w')

# 		cluster_id   = parse_cluster_id(cluster)
# 		cluster_size = 0

# 		cached_timestamp              = ''
# 		cached_event                  = ''
# 		cached_cluster_event          = ''
# 		cached_cluster_size           = ''
# 		cached_cluster_id_destination = ''

# 		for line in f_cluster:
			
# 			timestamp              = parse_timestamp(line)
# 			event, cluster_event   = parse_event(line)
# 			cluster_size  		   = cluster_size + parse_size(cluster_event, line)
# 			cluster_id_destination = parse_destination(cluster_event, line)


# 			print('---------------start-----------------------------')
# 			print (cluster_id + ' ' + timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') + ' ' + event)
# 			print('cluster_id = ' + cluster_id)
# 			print('cluster_size = ' + str(cluster_size))
# 			print('cluster_id_destination = ' + cluster_id_destination)
			


# 			if cluster_event == START: continue
# 			if cluster_event == END  : continue

# 			if cluster_event == T_ENTER or cluster_event == T_LEAVE:
# 				if cached_cluster_event == '':
# 					cached_timestamp     		  = timestamp
# 					cached_event         		  = event
# 					cached_cluster_event 		  = cluster_event
# 					cached_cluster_size  		  = cluster_size
# 					cached_cluster_id_destination = cluster_id_destination
# 					continue
# 				else:
# 					if cached_cluster_event == cluster_event and cached_timestamp == timestamp:
# 						cached_cluster_size = cached_cluster_size + cluster_size
# 						continue
# 					else:
# 						temp_timestamp 					= cached_timestamp
# 						temp_event 						= cached_event
# 						temp_cluster_event 				= cached_cluster_event
# 						temp_cluster_size 				= cached_cluster_size
# 						temp_cluster_id_destination 	= cached_cluster_id_destination

# 						cached_timestamp				= timestamp
# 						cached_event					= event
# 						cached_cluster_event			= cluster_event
# 						cached_cluster_size				= cluster_size
# 						cached_cluster_id_destination	= cluster_id_destination

# 						timestamp 						= temp_timestamp
# 						event 							= temp_event
# 						cluster_event 					= temp_cluster_event
# 						cluster_size 					= temp_cluster_size
# 						cluster_id_destination 			= temp_cluster_id_destination
# 			else:
# 				if cached_cluster_event != '':
# 					node = parse_node(cluster_id, cached_cluster_size, cached_timestamp)
# 					edge = parse_edge(cluster_id, cached_cluster_id_destination, cached_timestamp, cached_event)

# 					f_nodes.write(node)
# 					f_edges.write(edge)
# 					print ('node_c: ' + node)
# 					print ('edge_c: ' + edge)
# 					print('--------------------------------------------------')




# 			node = parse_node(cluster_id, cluster_size, timestamp)
# 			edge = parse_edge(cluster_id, cluster_id_destination, timestamp, event)


# 			if cluster_event == '':
# 				print ('node: ' + node)
# 			# f_nodes.write(node)

# 			if cluster_event == DISPERSE:
# 				print ('edge: ' + edge)
# 				# f_edges.write(edge)


			
# 			print('--------------------end------------------------------')
 


			
			


# 		f_cluster.close()
# 		f_nodes.close()
# 		f_edges.close()



# Identify the cluster information
def parse_cluster_id(filename): return filename[0:-4]
def parse_timestamp(line):      return datetime.strptime(line[0:19], '%Y-%m-%d %H:%M:%S')
def parse_event(line):          return string_to_relation(line[20:line.index('(')])



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

def parse_nodes(nodeId, nodeSizeBefore, nodeSizeAfter, timestamp, event, event_cache, timestamp_cache):

	if (event == START):    return []
	if (event == END)  :    return []

	if event_cache == T_LEAVE or event_cache == C_LEAVE: timestamp_cache = timestamp_cache + timedelta(minutes=rate)

	if (event == GROUP)   : return [parse_node(nodeId, nodeSizeAfter , timestamp)]
	if (event == DISPERSE): return [parse_node(nodeId, nodeSizeBefore, timestamp)]

	if (event == T_ENTER):
		if (timestamp != timestamp_cache):
			return [parse_node(nodeId, nodeSizeBefore, (timestamp - timedelta(minutes=rate))), parse_node(nodeId, nodeSizeAfter, timestamp)]
		else:
			return [parse_node(nodeId, nodeSizeAfter, timestamp)]

	if (event == T_LEAVE):
		if (timestamp != timestamp_cache - timedelta(minutes=rate)):
			return [parse_node(nodeId, nodeSizeBefore, timestamp), parse_node(nodeId, nodeSizeAfter, (timestamp + timedelta(minutes=rate)))]
		else:
			return [parse_node(nodeId, nodeSizeAfter, (timestamp + timedelta(minutes=rate)))]


	if (event == JOIN):     return [parse_node(nodeId, nodeSizeBefore, timestamp)]
	if (event == DETACH):   return [parse_node(nodeId, nodeSizeAfter, timestamp)]

	if  event == C_ENTER:
		if (timestamp != timestamp_cache):
			return [parse_node(nodeId, nodeSizeBefore, (timestamp - timedelta(minutes=rate))), parse_node(nodeId, nodeSizeAfter, timestamp)]
		else:
			return [parse_node(nodeId, nodeSizeAfter, timestamp)]
	if  event == C_LEAVE:
		if (timestamp != timestamp_cache - timedelta(minutes=rate)):
			return [parse_node(nodeId, nodeSizeBefore, timestamp), parse_node(nodeId, nodeSizeAfter, (timestamp + timedelta(minutes=rate)))]
		else:
			return [parse_node(nodeId, nodeSizeAfter, (timestamp + timedelta(minutes=rate)))]
	
	if  event == MERGE:     return [parse_node(nodeId, nodeSizeAfter, timestamp)]
	if  event == SPLIT:     return [parse_node(nodeId, nodeSizeBefore, timestamp)]



# Prepares a list of CSV entries for edges

def parse_edges(nodeId, supportingNodeId, timestamp, event):

	if (event == START):    return []
	if (event == END)  :    return []

	if (event == GROUP)   : return []
	if (event == DISPERSE): return []

	if (event == T_ENTER):  return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event))]
	if (event == T_LEAVE):  return [parse_edge(nodeId, nodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event))]

	if (event == JOIN):     return [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event))]
	if (event == DETACH):   return [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event))]

	if  event == C_ENTER:   return [parse_edge(nodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event))]
	if  event == C_LEAVE:   return [parse_edge(nodeId, nodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event))]
	
	if  event == MERGE:     return [parse_edge(supportingNodeId, nodeId, (timestamp - timedelta(minutes=rate)), timestamp, relation_to_string(event))]
	if  event == SPLIT:     return [parse_edge(nodeId, supportingNodeId, timestamp, (timestamp + timedelta(minutes=rate)), relation_to_string(event))]


def parse_continues(cluster_id, timestamp, timeline, event):

	if timeline == '': return []

	if (event == START): return  []
	if (event == END  ): return  []

	if (event == T_ENTER
	or 	event == C_IN
	or  event == DETACH
	or  event == C_ENTER
	or  event == GROUP
	or  event == MERGE):
		if timestamp > timeline + timedelta(minutes=rate): return [parse_continue(cluster_id, timeline, timestamp - timedelta(minutes=rate))]

	if (event == T_LEAVE
	or 	event == C_OUT
	or  event == JOIN
	or  event == C_LEAVE
	or  event == DISPERSE
	or  event == SPLIT):
		if timestamp > timeline: return [parse_continue(cluster_id, timeline, timestamp)]

	return []





# Creates the CSV entry for a node
def parse_node(nodeId, nodeSize, timestamp):
	return nodeId + ',' + str(nodeSize) + ',' + timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') + '\n'

# Creates the CSV entry for an edge
def parse_edge(nodeId, supportingNodeId, timestamp_start, timestamp_end, edgeName):
	return nodeId + ',' + supportingNodeId + ',' + timestamp_start.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + timestamp_end.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + edgeName + '\n'

# Creates the CSV entry for an continue
def parse_continue(nodeId, timestamp_start, timestamp_end):
	return parse_edge(nodeId, nodeId, timestamp_start, timestamp_end, 'CONTINUE')


# Writes each node in the CSV file
def write_nodes(nodes, f_nodes):
	for node in nodes: f_nodes.write(node);

# Writes each edge in the CSV file
def write_edges(edges, f_edges):
	for edge in edges: f_edges.write(edge);

# Writes each continue in the CSV file
def write_continues(continues, f_edges):
	write_edges(continues, f_edges)



def update_timeline(timestamp, event):

	if (event == START)   : return timestamp
	if (event == END)     : return timestamp

	if (event == GROUP)   : return timestamp
	if (event == DISPERSE): return timestamp + timedelta(minutes=rate)

	if (event == T_ENTER):  return timestamp
	if (event == T_LEAVE):  return timestamp + timedelta(minutes=rate)

	if (event == JOIN)  :   return timestamp + timedelta(minutes=rate)
	if (event == DETACH):   return timestamp

	if  event == C_ENTER:   return timestamp
	if  event == C_LEAVE:   return timestamp + timedelta(minutes=rate)
	
	if  event == MERGE:     return timestamp
	if  event == SPLIT:     return timestamp + timedelta(minutes=rate)






# # Clusters clusters based on the pattern of their sizes during their lifetimes.

# def process_size():

# 	datapoints = []

# 	clusters = identify_clusters(preprocessed2_dir)
# 	f_preprocessed = [open(preprocessed2_dir + cluster, 'r').readlines() for cluster in clusters]
# 	datapoints = [[format_datapoint(datapoint.split(',')) for datapoint in cluster] for cluster in f_preprocessed]

# 	distances = [[fastdtw(datapoint1, datapoint2, dist=euclidean)[0] for datapoint2 in datapoints] for datapoint1 in datapoints]

# 	db = DBSCAN(eps=1000, min_samples=3, metric="precomputed").fit(distances)

# 	print(db.labels_)


# # A helper function to format a datapoint
# def format_datapoint(datapoint):
# 	if datapoint == []: return []
# 	if datapoint == None: return None
# 	return [time.mktime(ciso8601.parse_datetime(datapoint[0]).timetuple()), int(datapoint[1])]
