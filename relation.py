import math

from constant import *

from activity import INVALID
from activity import STOP
from activity import MOVE


# Relation Names

INVALID           = 'invalid'

DISJOINT_STOP     = 'disjoint stop'
MEET              = 'meet'
ONE_WAY_APPROACH  = 'one way approach'
REVOLVE           = 'revolve'
ONE_WAY_MOVE_AWAY = 'one way move away'
TWO_WAY_APPROACH  = 'two way approach'
PARALLEL          = 'parallel'
TWO_WAY_MOVE_AWAY = 'two way move away'

ERROR             = 'error'


# Main
def process_relation(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j):
	relation = ''

	if(is_invalid(actv_i, actv_j)):
	  relation = INVALID
	elif(is_disjoint_stop(actv_i, actv_j, curr_coord_i, curr_coord_j)):
	  relation = DISJOINT_STOP
	elif(is_meet(actv_i, actv_j, curr_coord_i, curr_coord_j)):
	  relation = MEET
	elif(is_one_way_approach(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = ONE_WAY_APPROACH
	elif(is_revolve(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = REVOLVE
	elif(is_one_way_move_away(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = ONE_WAY_MOVE_AWAY
	elif(is_two_way_approach(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = TWO_WAY_APPROACH
	elif(is_parallel(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = PARALLEL
	elif(is_two_way_move_away(actv_i, actv_j, curr_coord_i, curr_coord_j, prev_coord_i, prev_coord_j)):
		relation = TWO_WAY_MOVE_AWAY
	else:
	  relation = ERROR

	return relation




# Tests

def is_invalid(actv_i, actv_j):
  if(actv_i == INVALID): return True
  if(actv_j == INVALID): return True
  return False

def is_disjoint_stop(actv_i, actv_j, coord_i, coord_j):
  if(actv_i == STOP and actv_j == STOP):
  	if(dist(coord_i, coord_j) > r_e): return True
  return False

def is_meet(actv_i, actv_j, coord_i, coord_j):
  if(actv_i == STOP and actv_j == STOP):
  	if(dist(coord_i, coord_j) <= r_e): return True
  return False




def is_one_way_approach(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if((actv_i == STOP and actv_j == MOVE) or
	   (actv_i == MOVE and actv_j == STOP)):
		if(dist(curr_coord_i, curr_coord_j) < dist(prev_coord_i, prev_coord_j)):
			return True
	return False

def is_revolve(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if((actv_i == STOP and actv_j == MOVE) or
	   (actv_i == MOVE and actv_j == STOP)):
		if(math.fabs(dist(curr_coord_i, curr_coord_j) - dist(prev_coord_i, prev_coord_j)) <= r_e):
			return True
	return False

def is_one_way_move_away(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if((actv_i == STOP and actv_j == MOVE) or
	   (actv_i == MOVE and actv_j == STOP)):
		if(dist(curr_coord_i, curr_coord_j) > dist(prev_coord_i, prev_coord_j)):
			return True
	return False




def is_two_way_approach(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if(actv_i == MOVE and actv_j == MOVE):
		if(dist(curr_coord_i, curr_coord_j) < dist(prev_coord_i, prev_coord_j)):
			return True
	return False

def is_parallel(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if(actv_i == MOVE and actv_j == MOVE):
		if(math.fabs(dist(curr_coord_i, curr_coord_j) == dist(prev_coord_i, prev_coord_j)) <= r_e):
			return True
	return False

def is_two_way_move_away(actv_i, actv_j, curr_coord_i, prev_coord_i, curr_coord_j, prev_coord_j):
	if(actv_i == MOVE and actv_j == MOVE):
		if(dist(curr_coord_i, curr_coord_j) > dist(prev_coord_i, prev_coord_j)):
			return True
	return False




# def is_one_way_move(actv_i, actv_j):
#   if(actv_i == 'stop' and actv_j == 'move'): return True
#   if(actv_i == 'move' and actv_j == 'stop'): return True
#   return False

# def is_one_way_move(actv_i, actv_j):
#   if(actv_i == 'stop' and actv_j == 'move'): return True
#   if(actv_i == 'move' and actv_j == 'stop'): return True
#   return False

# def is_two_way_move(actv_i, actv_j):
#   if(actv_i == 'move' and actv_j == 'move'): return True
#   return False