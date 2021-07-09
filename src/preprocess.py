from datetime import datetime
from constant import original_dir
from constant import preprocessed_dir
from file import identify_trajectories
import time


## Pre process files.
## Removes microsecond from datestamps


# Preprocess Microsoft Taxi dataset
def preprocess():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:
			
			datapoint  = line.split(',')
			_id        = datapoint[0]
			_timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S')
			_lat       = datapoint[3][0:-1] if '\n' in datapoint[3] else datapoint[3]  # removes '\n'
			_lon       = datapoint[2]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()


# Preprocess GeoLife dataset
def preprocess2():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:
			
			datapoint  = line.split(',')
			_id        = trajectory[0:3]
			_time      = datapoint[6][0:-2] if '\n' in datapoint[6] else datapoint[6]  # removes '\n'
			_timestamp = datetime.strptime(datapoint[5] + ' ' + _time, '%Y-%m-%d %H:%M:%S')
			_lat       = datapoint[0]
			_lon       = datapoint[1]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()


# Preprocess Rome Taxi dataset
def preprocess3():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:

			datapoint  = line.split(';')
			_id        = datapoint[0]
			_timestamp = datetime.strptime(datapoint[1], '%Y-%m-%d %H:%M:%S.%f+01')
			_point     = datapoint[2][6:-2].split(' ')
			_lat       = _point[0]
			_lon       = _point[1]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()




# Proprocess Patagonia Sheep dataset
def preprocess4():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:

			datapoint  = line.split(',')
			_id        = datapoint[8][2:-1]
			_timestamp = datetime.strptime(datapoint[2], '%Y-%m-%d %H:%M:%S.%f')
			_lat       = datapoint[4]
			_lon       = datapoint[3]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()



# Proprocess Galapagos Tortoise dataset
def preprocess5():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:

			datapoint  = line.split(',')
			_id        = datapoint[37][2:-1]
			_timestamp = datetime.strptime(datapoint[2], '%Y-%m-%d %H:%M:%S.%f')
			_lat       = datapoint[4]
			_lon       = datapoint[3]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()


# Proprocess Athens Truck dataset
def preprocess6():

	trajectories = identify_trajectories(original_dir)
	for trajectory in trajectories:

		f_original     = open(original_dir     + trajectory, 'r')
		f_preprocessed = open(preprocessed_dir + trajectory, 'w')

		for line in f_original:

			datapoint  = line.split(';')
			_id        = datapoint[0]
			_timestamp = datetime.strptime(datapoint[2] + ' ' + datapoint[3], '%d/%m/%Y %H:%M:%S')
			_lat       = datapoint[5]
			_lon       = datapoint[4]

			newline = _id + ',' + _timestamp.strftime('%Y-%m-%d %H:%M:%S') + ',' + _lat + ',' + _lon + '\n'
			f_preprocessed.write(newline)

		f_original.close()
		f_preprocessed.close()



if __name__ == '__main__':
	preprocess2()