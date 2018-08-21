import math

from constant import *

# Activity Names

INVALID = 'invalid'
STOP    = 'stop'
MOVE    = 'move'

ERROR   = 'error'



# Main Tests
def process_activity(curr_coord, prev_coord):
	activity = ''

	if(is_invalid(curr_coord, prev_coord)):
		activity = INVALID
	elif(is_stop(curr_coord, prev_coord)):
		activity = STOP
	elif(is_move(curr_coord, prev_coord)):
		activity = MOVE
	else:
		activity = ERROR

	return activity





# Tests

def is_invalid(curr_coord, prev_coord):
	if(prev_coord[0] == '' or prev_coord[1] == ''):
		return True
	else:
		return False


def is_stop(curr_coord, prev_coord):
	if(math.fabs(curr_coord[0] - prev_coord[0]) <= r_e and
     math.fabs(curr_coord[1] - prev_coord[1]) <= r_e):
		return True
	else:
		return False


def is_move(curr_coord, prev_coord):
	if(math.fabs(curr_coord[0] - prev_coord[0]) > r_e or
     math.fabs(curr_coord[1] - prev_coord[1]) > r_e):
		return True
	else:
		return False



# DEPRECATED
# def is_stop(curr_lat, curr_lon, prev_lat, prev_lon):

# 	if(curr_lat == '' or curr_lon == ''): return False
# 	if(prev_lat == '' or prev_lon == ''): return False

# 	if(math.fabs(curr_lat - prev_lat) <= r_e and
#    	math.fabs(curr_lon - prev_lon) <= r_e):
# 		return True
# 	else:
# 		return False


# def is_move(curr_lat, curr_lon, prev_lat, prev_lon):

#  	if(curr_lat == '' or curr_lon == ''): return False
# 	if(prev_lat == '' or prev_lon == ''): return False

# 	if(math.fabs(curr_lat - prev_lat) > r_e or
#      math.fabs(curr_lon - prev_lon) > r_e):
# 		return True
# 	else:
# 		return False

