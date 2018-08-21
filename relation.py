from constant import *

# Relation Names

INVALID       = 'invalid'
DISJOINT_STOP = 'disjoint stop'
MEET          = 'meet'
ONE_WAY_MOVE  = 'one way move'
TWO_WAY_MOVE  = 'two way move'

ERROR         = 'error'


# Main
def process_relation(actv_i, actv_j, coord_i, coord_j):
	relation = ''

	if(is_invalid(actv_i, actv_j)):
	  relation = INVALID
	elif(is_disjoint_stop(actv_i, actv_j, coord_i, coord_j)):
	  relation = DISJOINT_STOP
	elif(is_meet(actv_i, actv_j, coord_i, coord_j)):
	  relation = MEET
	elif(is_one_way_move(actv_i, actv_j)):
	  relation = ONE_WAY_MOVE
	elif(is_two_way_move(actv_i, actv_j)):
	  relation = TWO_WAY_MOVE
	else:
	  relation = ERROR

	return relation




# Tests

def is_invalid(actv_i, actv_j):
  if(actv_i == 'invalid'): return True
  if(actv_j == 'invalid'): return True
  return False

def is_disjoint_stop(actv_i, actv_j, coord_i, coord_j):
  if(actv_i == 'stop' and actv_j == 'stop'):
  	if(dist(coord_i, coord_j) > r_e): return True
  return False

def is_meet(actv_i, actv_j, coord_i, coord_j):
  if(actv_i == 'stop' and actv_j == 'stop'):
  	if(dist(coord_i, coord_j) <= r_e): return True
  return False

def is_one_way_move(actv_i, actv_j):
  if(actv_i == 'stop' and actv_j == 'move'): return True
  if(actv_i == 'move' and actv_j == 'stop'): return True
  return False

def is_two_way_move(actv_i, actv_j):
  if(actv_i == 'move' and actv_j == 'move'): return True
  return False