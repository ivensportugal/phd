import os
from datetime import datetime

from activity import process_activity

from relation import process_relation
from relation import INVALID
from relation import DISJOINT_STOP
from relation import MEET
from relation import ONE_WAY_MOVE
from relation import TWO_WAY_MOVE

from constant import file_suffix
from constant import original_dir
from constant import processed_a_dir
from constant import processed_r_dir
from constant import processed_prefix
from constant import eps
from constant import min_samples

import numpy as np
from sklearn.cluster import DBSCAN




def identify_trajectories():
  files = []
  for file in os.listdir(original_dir):
    if file.endswith(file_suffix):
      files.append(file)
  return files

def identify_relations():
  files = []
  for file in os.listdir(processed_r_dir):
    if file.endswith(file_suffix):
      files.append(file)
  return files


def create_processed_a_dir():
  if not os.path.exists(processed_a_dir):
    os.makedirs(processed_a_dir)

def create_processed_r_dir():
  if not os.path.exists(processed_r_dir):
    os.makedirs(processed_r_dir)



def to_minutes(minutes_s):

  minutes_f = 0

  try: minutes_f = float(minutes_s)
  except ValueError, Argument: minutes_f = ''

  return minutes_f





def process_activities(trajectories):

  for trajectory in trajectories:

    print("Processing " + trajectory)

    f_original  = open(original_dir  + trajectory, 'r')
    f_processed = open(processed_a_dir + processed_prefix + trajectory, 'w')

    prev_datapoint = ['','','','']

    for line in f_original:

      curr_datapoint = line.split(',')

      curr_coord = []
      prev_coord = []

      curr_coord.insert(0, to_minutes(curr_datapoint[3]))
      curr_coord.insert(1, to_minutes(curr_datapoint[2]))
      prev_coord.insert(0, to_minutes(prev_datapoint[3]))
      prev_coord.insert(1, to_minutes(prev_datapoint[2]))

      activity = process_activity(curr_coord, prev_coord)
      

      newline = line.replace(line[-2:-1], ',' + activity)

      f_processed.write(newline)

      prev_datapoint = curr_datapoint

    f_processed.close()
    f_original.close()





def process_relations(trajectories):

  for pos_i, traj_i in enumerate(trajectories):
    for pos_j, traj_j in enumerate(trajectories):

      if(pos_j <= pos_i): continue

      print("Processing " + traj_i + " - " + traj_j)

      f_processed = open(processed_r_dir + processed_prefix + traj_i + "-" + traj_j , 'w')

      f_i = open(processed_a_dir + processed_prefix + traj_i)
      f_j = open(processed_a_dir + processed_prefix + traj_j)

      line_i = f_i.readline()
      line_j = f_j.readline()

      # Two indexes: i points to the points of traj_i, and j to points of traj_j
      # Traverse both trajectories, recording relationships

      while(line_i != '' and line_j != ''):

        datapoint_i = line_i.split(',')
        datapoint_j = line_j.split(',')

        coord_i = []
        coord_j = []

        coord_i.insert(0, to_minutes(datapoint_i[3]))
        coord_i.insert(1, to_minutes(datapoint_i[2]))
        coord_j.insert(0, to_minutes(datapoint_j[3]))
        coord_j.insert(1, to_minutes(datapoint_j[2]))


        actv_i = datapoint_i[4][0:-1] #removes '/n'
        actv_j = datapoint_j[4][0:-1] #removes '/n'


        relation = process_relation(actv_i, actv_j, coord_i, coord_j)

     
        timestamp_i = datetime.strptime(datapoint_i[1], '%Y-%m-%d %H:%M:%S')
        timestamp_j = datetime.strptime(datapoint_j[1], '%Y-%m-%d %H:%M:%S')



        # Result and Update

        newline = ''

        if(timestamp_i < timestamp_j):
          newline = traj_i + "," + traj_j + "," + datapoint_i[1] + "," + relation + '\n'
          line_i = f_i.readline()
        elif(timestamp_i > timestamp_j):
          newline = traj_i + "," + traj_j + "," + datapoint_j[1] + "," + relation + '\n'
          line_j = f_j.readline()
        elif(timestamp_i == timestamp_j):
          newline = traj_i + "," + traj_j + "," + datapoint_i[1] + "," + relation + '\n'
          line_i = f_i.readline()
          line_j = f_j.readline()
        else:
          continue

        f_processed.write(newline)
      

      relation = INVALID
      while(line_i != ''):
        datapoint_i = line_i.split(',')
        f_processed.write(traj_i + "," + traj_j + "," + datapoint_i[1] + "," + relation + '\n')
        line_i = f_i.readline()

      while(line_j != ''):
        datapoint_j = line_j.split(',')
        f_processed.write(traj_i + "," + traj_j + "," + datapoint_j[1] + "," + relation + '\n')
        line_j = f_j.readline()

      f_processed.close()




def analyze_relations(relations, relation_interest):


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
    traj_satisfy = []
    traj_satisfy.extend(
      [[datapoints_satisfy[i][0], datapoints_satisfy[i][2]] for i,x in enumerate(labels) if x == valid_cluster])
    traj_satisfy.extend(
      [[datapoints_satisfy[i][1], datapoints_satisfy[i][2]] for i,x in enumerate(labels) if x == valid_cluster])

    print('results for cluster id = ' + str(valid_cluster))
    print('Around ' + (datapoints_satisfy[np.where(labels == valid_cluster)[0][0]][2]).strftime("%Y-%m-%d %H:%M:%S"))
    for traj in set([row[0] for row in traj_satisfy]):
      print(traj)

  






def main():
  trajectories = identify_trajectories()
  create_processed_a_dir()
  process_activities(trajectories)
  create_processed_r_dir()
  process_relations(trajectories)
  relations = identify_relations()
  analyze_relations(relations, MEET)


if __name__ == '__main__':
  main()