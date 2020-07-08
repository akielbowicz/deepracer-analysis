from time import time
import math

def reward_function_completelap_slowly(params):
    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']

    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Give a very low reward by default
    reward = 1e-3

    # Give a high reward if no wheels go off the track and
    # the agent is somewhere in between the track borders
    if all_wheels_on_track and (0.5 * track_width - distance_from_center) >= 0.05:
        reward = 1.0

    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward = 1.0
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3  # likely crashed/ close to off track

    # We don't want the car to go any faster at this point
    SPEED_THRESHOLD = 2.0

    # Penalize reward if the agent is steering too much
    if speed >= SPEED_THRESHOLD:
        reward *= 0.01

    return float(reward)

def reward_function(params):
    # written this way to make it easier to use the rest in the log analysis notebooks
    # return reward_function_waypoints(params)
    # return reward_function_progress(params)
    # return reward_function_completelap(params)
    return reward_function_completelap_slowly(params)