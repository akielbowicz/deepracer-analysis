# v2
import math

max_speed = 4.0

x_coord = 0
y_coord = 1

def circular_next_waypoint_after( index, wpts ):
	# we just need to make sure we wrap around at the end as i'm not sure how this works in deepracer when the car finishes one lap (and cannot debug!)
	if index < len(wpts) - 1:
		return index + 1
	else:
		return 0

# each line is [ [x1,y1], [x2,y2] ]
def angle_between( line1, line2 ):
	line1_rad = math.atan2(line1[1][y_coord] - line1[0][y_coord], line1[1][x_coord] - line1[0][x_coord])
	line2_rad = math.atan2(line2[1][y_coord] - line2[0][y_coord], line2[1][x_coord] - line2[0][x_coord])
	
	line1_angle = math.degrees(line1_rad)
	line2_angle = math.degrees(line2_rad)

	diff = abs(line1_angle - line2_angle)

	if diff > 180:
		diff = 360 - diff

	return diff	

def line_from( start_pos, end_pos ):
	return [ start_pos, end_pos ]

def reward_function(params):
	waypoints = params['waypoints']
	closest_waypoints_indices = params['closest_waypoints']
	heading = params['heading']
	reward = 1.0 if params['all_wheels_on_track'] else -0.01
	current_pos = [ params['x'], params['y'] ]

	next_point_index = closest_waypoints_indices[1]
	behind_point_index = closest_waypoints_indices[0]

	next_point_pos = waypoints[next_point_index]
	behind_point_pos = waypoints[behind_point_index]

	# look ahead to the following waypoint
	next_next_point_index = circular_next_waypoint_after(next_point_index, waypoints)
	next_next_point_pos = waypoints[ next_next_point_index ]

	# Calculate the direction in radians, arctan2(dy, dx), the result is (-pi, pi) in radians
	track_direction = math.atan2(next_next_point_pos[y_coord] - behind_point_pos[y_coord], next_next_point_pos[x_coord] - behind_point_pos[x_coord]) 

	# Convert to degrees
	track_direction = math.degrees(track_direction)

	# Calculate the difference between the track direction and the heading direction of the car
	direction_diff = abs(track_direction - heading)
	if direction_diff > 180:
		direction_diff = 360 - direction_diff

	# Penalize the reward if the difference is too large
	DIRECTION_THRESHOLD = 10.0

	if direction_diff > DIRECTION_THRESHOLD:
		reward *= 0.5

	# work out what the curve looks like ahead of us
	curve_angle = angle_between( line_from(next_next_point_pos, next_point_pos), line_from(next_point_pos, behind_point_pos ) )

	# schumacher mode on
	safe_max_speed = max_speed

	if curve_angle > 20:
		safe_max_speed = 1.0
	elif curve_angle > 10:
		safe_max_speed = max_speed * 0.5
	elif curve_angle > 5:
		safe_max_speed = max_speed

	if params['speed'] > safe_max_speed:
		speed_penalty = 0.3
	else:
		speed_penalty = (params['speed'] / max_speed)

	reward *= speed_penalty
	reward += ( params['progress']**1.61 - params['steps'] )/ 300 if int(params['progress'] % 5 ) == 0 else 0.0

	return float(reward)