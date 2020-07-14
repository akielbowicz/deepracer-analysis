from math import atan2, degrees, pi

def reward_function(params):
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    steps = params['steps']
    progress = params['progress']

    reward = progress / steps * 10

     # Calculate the direction of the center line based on the closest waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]) 
    # Convert to degree
    track_direction = degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 21.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= -0.5

    # We don't want the car to go any faster at this point
    SPEED_THRESHOLD = 2.0

    # Penalize reward very harshly if the agent is going too fast
    if speed >= SPEED_THRESHOLD:
        reward = abs(reward) * -1.0

    if not all_wheels_on_track:
        reward = abs(reward) * -2.0

    return float(reward)