# v5
from time import time
import math

max_speed = 4.0
x_coord = 0
y_coord = 1

def circular_next_waypoint_after( index, wpts ):
    # we just need to make sure we wrap around at the end as i'm not sure how this works in deepracer when the car finishes one lap (and cannot debug!)
    if index < len(wpts) - 1:
        return index + 1
    else:
        return 0# each line is [ [x1,y1], [x2,y2] ]
    
def angle_between( line1, line2 ):
    line1_rad = math.atan2(line1[1][y_coord] - line1[0][y_coord], line1[1][x_coord] - line1[0][x_coord])
    line2_rad = math.atan2(line2[1][y_coord] - line2[0][y_coord], line2[1][x_coord] - line2[0][x_coord])
    diff = line1_rad - line2_rad
    if diff < 0:
        diff += math.pi * 2 
    
    # radians to degrees
    diff = math.degrees(diff)
    if diff > 180:
        diff = 360 - diff
    return diff
        
def line_from( start_pos, end_pos ):
    return [ start_pos, end_pos ]
    
def reward_function_waypoints(params):
    waypoints = params['waypoints']
    closest_waypoints_indices = params['closest_waypoints']
    heading = params['heading']
    reward = 1.0 # if params['all_wheels_on_track'] else 1e-6
    current_pos = [ params['x'], params['y'] ]
    next_point_index = closest_waypoints_indices[1]
    behind_point_index = closest_waypoints_indices[0]    
    next_point_pos = waypoints[next_point_index]
    behind_point_pos = waypoints[behind_point_index]    # look ahead to the following waypoints
    next_next_point_index = circular_next_waypoint_after(next_point_index, waypoints)
    next_next_next_point_index = circular_next_waypoint_after(next_next_point_index, waypoints)
    next_next_point_pos = waypoints[ next_next_point_index ]
    next_next_next_point_pos = waypoints[ next_next_next_point_index ]    # Calculate the direction in radians, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point_pos[y_coord] - behind_point_pos[y_coord], next_point_pos[x_coord] - behind_point_pos[x_coord])     # Convert to degrees
    track_direction = math.degrees(track_direction)    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff    # Penalize the reward if the difference is too large but give room to take better paths
    DIRECTION_THRESHOLD = 20.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.8    # work out what the curve looks like ahead of us
    curve_angle = angle_between( line_from(next_next_next_point_pos, next_next_point_pos), line_from(next_next_point_pos, next_point_pos ) )    # schumacher mode on
    safe_max_speed = max_speed    
    if curve_angle > 20:
        safe_max_speed = 1.0
    elif curve_angle > 5:
        safe_max_speed = max_speed * 0.5    
    
    if params['speed'] > safe_max_speed:
            speed_penalty = 0.1 # very likely to crash in the next couple of steps so penalize a lot
    else:
        if curve_angle < 1:
            if params['speed'] == max_speed:
                # clearly we need to be going at top speed, so we give extra incentive (not a penalty in this case)
                speed_penalty = 2.0
            else:
                speed_penalty = -1.0
        else:
            speed_penalty = (params['speed'] / max_speed) ** 2
    reward *= speed_penalty
    if params['progress'] == 100:
        reward += 100 * params['progress'] / params['steps']
    trace_log = f'"reward":{reward},"curve_angle":{curve_angle},"speed_penalty":{speed_penalty},"safe_max_speed":{safe_max_speed},"direction_diff":{direction_diff}'
    print(f'REWARD_TRACE_LOG:{trace_log}')
    return float(reward)

def reward_function_progress(params):
    heading = params['heading']
    steering = params['steering_angle']
    speed = params['speed']
    steps = params['steps']
    progress = params['progress']
    waypoints = params['waypoints']
    closest_waypoints_indices = params['closest_waypoints']    
    next_point_index = closest_waypoints_indices[1]
    behind_point_index = closest_waypoints_indices[0]
    next_point_pos = waypoints[next_point_index]
    behind_point_pos = waypoints[behind_point_index]    # Calculate the direction in radians, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point_pos[y_coord] - behind_point_pos[y_coord], next_point_pos[x_coord] - behind_point_pos[x_coord])     # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff
    reward = progress / steps if steps > 0 and direction_diff <= 20 else 1e-6
    trace_log = f'"reward":{reward},"track_direction":{track_direction},"direction_diff":{direction_diff}'
    print(f'REWARD_TRACE_LOG:{trace_log}')
    return reward

def reward_function(params):    # written this way to make it easier to use the rest in the log analysis notebooks
    #return reward_function_waypoints(params)
    return reward_function_progress(params)