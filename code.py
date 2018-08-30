import os
from datetime import datetime

from activity import process_activity
from relation import process_relation
from analysis import analyze_relations

from relation import INVALID

from constant import file_suffix
from constant import original_dir
from constant import processed_a_dir
from constant import processed_r_dir
from constant import processed_prefix
from constant import eps
from constant import min_samples




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

      prev_datapoint_i = ['','','','','']
      prev_datapoint_j = ['','','','','']

      while(line_i != '' and line_j != ''):

        curr_datapoint_i = line_i.split(',')
        curr_datapoint_j = line_j.split(',')

        curr_coord_i = []
        curr_coord_j = []

        prev_coord_i = []
        prev_coord_j = []

        curr_coord_i.insert(0, to_minutes(curr_datapoint_i[3]))
        curr_coord_i.insert(1, to_minutes(curr_datapoint_i[2]))
        curr_coord_j.insert(0, to_minutes(curr_datapoint_j[3]))
        curr_coord_j.insert(1, to_minutes(curr_datapoint_j[2]))

        prev_coord_i.insert(0, to_minutes(prev_datapoint_i[3]))
        prev_coord_i.insert(1, to_minutes(prev_datapoint_i[2]))
        prev_coord_j.insert(0, to_minutes(prev_datapoint_j[3]))
        prev_coord_j.insert(1, to_minutes(prev_datapoint_j[2]))


        actv_i = curr_datapoint_i[4][0:-1] #removes '/n'
        actv_j = curr_datapoint_j[4][0:-1] #removes '/n'


        relation = process_relation(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j)

     
        timestamp_i = datetime.strptime(curr_datapoint_i[1], '%Y-%m-%d %H:%M:%S')
        timestamp_j = datetime.strptime(curr_datapoint_j[1], '%Y-%m-%d %H:%M:%S')



        # Result and Update

        newline = ''

        if(timestamp_i < timestamp_j):
          newline = traj_i + "," + traj_j + "," + curr_datapoint_i[1] + "," + relation + '\n'
          line_i = f_i.readline()
        elif(timestamp_i > timestamp_j):
          newline = traj_i + "," + traj_j + "," + curr_datapoint_j[1] + "," + relation + '\n'
          line_j = f_j.readline()
        elif(timestamp_i == timestamp_j):
          newline = traj_i + "," + traj_j + "," + curr_datapoint_i[1] + "," + relation + '\n'
          line_i = f_i.readline()
          line_j = f_j.readline()
        else:
          continue

        f_processed.write(newline)

        prev_datapoint_i = curr_datapoint_i
        prev_datapoint_j = curr_datapoint_j
      

      relation = INVALID
      while(line_i != ''):
        curr_datapoint_i = line_i.split(',')
        f_processed.write(traj_i + "," + traj_j + "," + curr_datapoint_i[1] + "," + relation + '\n')
        line_i = f_i.readline()

      while(line_j != ''):
        curr_datapoint_j = line_j.split(',')
        f_processed.write(traj_i + "," + traj_j + "," + curr_datapoint_j[1] + "," + relation + '\n')
        line_j = f_j.readline()

      f_processed.close()






def main():
  #trajectories = identify_trajectories()
  #create_processed_a_dir()
  #process_activities(trajectories)
  #create_processed_r_dir()
  #process_relations(trajectories)
  relations = identify_relations()
  analyze_relations(relations)


if __name__ == '__main__':
  main()