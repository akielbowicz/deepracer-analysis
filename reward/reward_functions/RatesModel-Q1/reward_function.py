import math
import logging

logger = logging.getLogger('reward_function')

def reward_function(params): 
    logger.info(params)
    
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    max_speed = 4.0  
    reward = 1.0    # Calculate the direction of the center line based on the direction between where we're currently at and the next waypoint
    next_point = waypoints[closest_waypoints[1]]
    prev_point = [params['y'],params['x']]    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]) 
    # Convert to degree
    track_direction = math.degrees(track_direction)    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 10.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5    # lower reward for slowness
    reward *= (params['speed'] / max_speed) ** 2    
    return float(reward)