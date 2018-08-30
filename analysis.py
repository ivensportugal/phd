import os
from datetime import datetime

from constant import processed_r_dir
from constant import eps
from constant import min_samples

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



def analyze_relations(relations):

  analyze_relation(relations, MEET)


def analyze_relation(relations, relation_interest):


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


  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  X = [[(row[2] - datetime(1970,1,1)).total_seconds()] for row in datapoints_satisfy]
  if(X == []): return
  db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

  labels = db.labels_

  # Results
  valid_clusters = set(labels)
  valid_clusters.discard(-1)  # Removes points without cluster
  for valid_cluster in valid_clusters:
    relation_satisfy = []
    relation_satisfy.extend(
      [[datapoints_satisfy[i][2], datapoints_satisfy[i][0], datapoints_satisfy[i][1]] for i,x in enumerate(labels) if x == valid_cluster])


    timestamps = [row[2] for row in datapoints_satisfy]
    timestamps = list(set(timestamps))
    timestamps.sort()

    edges = []
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





