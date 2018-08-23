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
	if(dist(curr_coord, prev_coord) <= r_e):
		return True
	else:
		return False

def is_move(curr_coord, prev_coord):
	if(dist(curr_coord, prev_coord) > r_e):
		return True
	else:
		return False
