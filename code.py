import math
import os

# Constants
r_e = 0.016
r_n = 0.030


def is_stop(curr_lat, curr_lon, prev_lat, prev_lon):

  if(curr_lat == '' or curr_lon == ''): return False
  if(prev_lat == '' or prev_lon == ''): return False

  if(math.fabs(curr_lat - prev_lat) <= r_e and
     math.fabs(curr_lon - prev_lon) <= r_e):
    return True
  else:
    return False



def is_move(curr_lat, curr_lon, prev_lat, prev_lon):

  if(curr_lat == '' or curr_lon == ''): return False
  if(prev_lat == '' or prev_lon == ''): return False

  if(math.fabs(curr_lat - prev_lat) > r_e or
     math.fabs(curr_lon - prev_lon) > r_e):
    return True
  else:
    return False




def identify_trajectories():
  files = []
  for file in os.listdir('./originals/'):
    if file.endswith('.txt'):
      files.append(file)
  return files


def create_processed_dir():
  processed_dir = './processed/'
  if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
  return processed_dir



def convert_coordinates(curr_lat, curr_lon, prev_lat, prev_lon):

  return_curr_lat = 0
  return_curr_lon = 0
  return_prev_lat = 0
  return_prev_lon = 0

  try: return_curr_lat = float(curr_lat)
  except ValueError, Argument: return_curr_lat = ''

  try: return_curr_lon = float(curr_lon)
  except ValueError, Argument: return_curr_lon = ''

  try: return_prev_lat = float(prev_lat)
  except ValueError, Argument: return_prev_lat = ''

  try: return_prev_lon = float(prev_lon)
  except ValueError, Argument: return_prev_lon = ''

  return (return_curr_lat, return_curr_lon, return_prev_lat, return_prev_lon)




def process_trajectories(trajectories, processed_dir):

  for trajectory in trajectories:

    original_dir = './originals/'

    f_original  = open(original_dir  + trajectory, 'r')
    f_processed = open(processed_dir + 'p' + trajectory, 'w')

    prev_datapoint = ['','','','']

    for line in f_original:

      curr_datapoint = line.split(',')

      activity = 'invalid'

      curr_lat, curr_lon, prev_lat, prev_lon = convert_coordinates(curr_datapoint[3],
                                                                   curr_datapoint[2],
                                                                   prev_datapoint[3],
                                                                   prev_datapoint[2])

      if(is_stop(curr_lat, curr_lon, prev_lat, prev_lon)):
        activity = 'stop'
      elif(is_move(curr_lat, curr_lon, prev_lat, prev_lon)):
        activity = 'move'

      newline = line.replace(line[-2:-1], ',' + activity)

      f_processed.write(newline)

      prev_datapoint = curr_datapoint

    f_processed.close()
    f_original.close()



trajectories = identify_trajectories()
processed_dir = create_processed_dir()
process_trajectories(trajectories, processed_dir)