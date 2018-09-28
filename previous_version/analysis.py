import os
from datetime import datetime

from constant import processed_a_dir
from constant import processed_r_dir
from constant import processed_prefix
from constant import eps
from constant import min_samples
from constant import dist
from constant import r_ct
from constant import r_cl

from relation import DISJOINT_STOP
from relation import MEET
from relation import ONE_WAY_APPROACH
from relation import REVOLVE
from relation import ONE_WAY_MOVE_AWAY
from relation import TWO_WAY_APPROACH
from relation import PARALLEL
from relation import TWO_WAY_MOVE_AWAY

import numpy as np
from sklearn.cluster import DBSCAN

import graph



def analyze_relations(relations, trajectories):

  analyze_relation(relations, trajectories, MEET)


def analyze_relation(relations, trajectories, relation_interest):

  datapoints_satisfy  = find_datapoints_satisfy(relations, relation_interest)
  db_result           = run_dbscan(datapoints_satisfy)
  subgraphs_result    = find_subgraphs(db_result, datapoints_satisfy)
  subgraphs_result    = calculate_centroids(subgraphs_result)
  centroids_avg       = calculate_centroids_avg(subgraphs_result)
  report_statistics(centroids_avg, trajectories)



def find_datapoints_satisfy(relations, relation_interest):

  datapoints_satisfy = []   # clustering datapoints

  for relation_ in relations:

    print('Analyzing ' + relation_)

    f_analysis  = open(processed_r_dir + relation_, 'r')
    

    for line in f_analysis:

      datapoint = line.split(',')
      traj_i    = datapoint[0]
      traj_j    = datapoint[1]
      timestamp = datetime.strptime(datapoint[2], '%Y-%m-%d %H:%M:%S') # to datetime
      relation  = datapoint[3][0:-1] #removes '/n'

      if(relation == relation_interest):
        datapoints_satisfy.append([traj_i, traj_j, timestamp])

  return datapoints_satisfy



def run_dbscan(datapoints_satisfy):

  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  X = [[(row[2] - datetime(1970,1,1)).total_seconds()] for row in datapoints_satisfy]
  if(X == []): return
  db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

  return db


def find_subgraphs(db, datapoints_satisfy):

  labels = db.labels_

  subgraphs_result      = []
  timestamp_dict_result = {}


  # Results
  valid_clusters = set(labels)
  valid_clusters.discard(-1)  # Removes points without cluster
  for valid_cluster in valid_clusters:
    print("******************** Results for cluster " + str(valid_cluster) + " ********************")
    relation_satisfy = []
    relation_satisfy.extend(
      [[datapoints_satisfy[i][2], datapoints_satisfy[i][0], datapoints_satisfy[i][1]] for i,x in enumerate(labels) if x == valid_cluster])


    timestamps = [row[2] for row in datapoints_satisfy]
    timestamps = list(set(timestamps))
    timestamps.sort()

    edges = []
    timestamp_dict_result = {}
    for timestamp in timestamps:
      edges = [[row[0], row[1]] for row in datapoints_satisfy if row[2] == timestamp]

      unique_edges = []
      unique_edges.extend([row[0] for row in edges])
      unique_edges.extend([row[1] for row in edges])

      # graph operations
      g = graph.Graph(list(set(unique_edges)))
      for edge in edges:
        g.addEdge(edge[0], edge[1])

      subgraphs = g.subgraphs()
      if(len(subgraphs) > 0):
        print(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        print(subgraphs)

      timestamp_dict_result[timestamp] = subgraphs

    subgraphs_result.append(timestamp_dict_result)

  return subgraphs_result




def calculate_centroids(list_of_clusters):

  for cluster in list_of_clusters:

    for timestamp in cluster:
      
      for i, subgraph in enumerate(cluster[timestamp]):

        centroid = calculate_centroid(timestamp, subgraph)
        cluster[timestamp][i] = (subgraph, centroid)


  return list_of_clusters


def calculate_centroid(timestamp_cluster, subgraph):


  latitude_sum  = 0
  longitude_sum = 0
  num_traj = len(subgraph)

  for traj in subgraph:

    f_centroid = open(processed_a_dir + processed_prefix + traj)

    latitude  = 0
    longitude = 0

    for line in f_centroid:
      datapoint = line.split(',')
      timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S') # to datetime

      if(timestamp > timestamp_cluster): break

      latitude  = float(datapoint[3])
      longitude = float(datapoint[2])

    latitude_sum  += latitude
    longitude_sum += longitude

  return [latitude_sum/num_traj, longitude_sum/num_traj]




def calculate_centroids_avg(list_of_clusters):

  centroids_avg = []

  for cluster in list_of_clusters:

    centroid_avg = []  # [[avg_lat, avg_lon], [start_timestamp, end_timestamp], num_centroids]

    for timestamp in cluster:
      
      for subgraph in cluster[timestamp]:

        if(len(centroid_avg) == 0):

          centroid_avg_lat = subgraph[1][0]
          centroid_avg_lon = subgraph[1][1]
          centroid_avg.append([[centroid_avg_lat, centroid_avg_lon],[timestamp,timestamp],1])

        else:

          belongs_to_a_centroid_avg = False;

          for i, centroid in enumerate(centroid_avg):

            if(dist(subgraph[1], centroid[0]) <= r_ct):

              belongs_to_a_centroid_avg = True;

              centroid_avg_lat = centroid_avg[i][0][0]
              centroid_avg_lon = centroid_avg[i][0][1]
              n = centroid[2]

              centroid_avg_lat = (float(n)/(n+1) * centroid_avg_lat) + (subgraph[1][0] / (n+1))
              centroid_avg_lon = (float(n)/(n+1) * centroid_avg_lon) + (subgraph[1][1] / (n+1))

              centroid_avg[i][0][0] = centroid_avg_lat
              centroid_avg[i][0][1] = centroid_avg_lon
              centroid_avg[i][1][1] = timestamp
              centroid_avg[i][2]   += 1

              break

          
          if(not belongs_to_a_centroid_avg):

            centroid_avg_lat = subgraph[1][0]
            centroid_avg_lon = subgraph[1][1]
            centroid_avg.append([[centroid_avg_lat, centroid_avg_lon],[timestamp,timestamp],1])


  return centroid_avg



def report_statistics(centroids_avg, trajectories):

  for centroid in centroids_avg:

    trajs_in_cluster = []
    flow_in  = 0
    flow_out = 0

    for trajectory in trajectories:

      f_processed = open(processed_a_dir + processed_prefix + trajectory, 'r')

      for line in f_processed:

        datapoint = line.split(',')
        timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S') # to datetime

        if(timestamp >= centroid[1][0] and timestamp <= centroid[1][1]):

          coord = [datapoint[3], datapoint[2]]
          if(dist(coord, centroid[0]) <= r_cl and trajectory not in trajs_in_cluster):
            flow_in += 1
            trajs_in_cluster.append(trajectory)

          elif(dist(coord, centroid[0]) > r_cl and trajectory in trajs_in_cluster):
            flow_out -= 1
            trajs_in_cluster = trajs_in_cluster.remove(trajectory)

    print('-----------------------')
    print(centroid)
    print('--')
    print(flow_in)
    print(flow_out)
    print('-----------------------')





  



























# def analyze_relation(relations, relation_interest):


#   datapoints_satisfy = []   # clustering datapoints

#   for relation_ in relations:

#     print('Analyzing ' + relation_)

#     f_analysis  = open(processed_r_dir + relation_, 'r')
    

#     for line in f_analysis:

#       datapoint = line.split(',')
#       traj_i    = datapoint[0]
#       traj_j    = datapoint[1]
#       timestamp = datetime.strptime(datapoint[2], '%Y-%m-%d %H:%M:%S') # to datetime
#       relation  = datapoint[3][0:-1] #removes '/n'

#       if(relation == relation_interest):
#         datapoints_satisfy.append([traj_i, traj_j, timestamp])


#   ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
#   X = [[(row[2] - datetime(1970,1,1)).total_seconds()] for row in datapoints_satisfy]
#   if(X == []): return
#   db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

#   labels = db.labels_

#   # Results
#   valid_clusters = set(labels)
#   valid_clusters.discard(-1)  # Removes points without cluster
#   for valid_cluster in valid_clusters:
#     traj_satisfy = []
#     traj_satisfy.extend(
#       [[datapoints_satisfy[i][0], datapoints_satisfy[i][2]] for i,x in enumerate(labels) if x == valid_cluster])
#     traj_satisfy.extend(
#       [[datapoints_satisfy[i][1], datapoints_satisfy[i][2]] for i,x in enumerate(labels) if x == valid_cluster])

#     print('results for cluster id = ' + str(valid_cluster))
#     print('Around ' + (datapoints_satisfy[np.where(labels == valid_cluster)[0][0]][2]).strftime("%Y-%m-%d %H:%M:%S"))
#     for traj in set([row[0] for row in traj_satisfy]):
#       print(traj)





