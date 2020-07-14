# v8
from time import time
from math import atan2, degrees, pi
from sys import stderr

max_speed = 4.0

x_coord = 0
y_coord = 1

# each line is [ [x1,y1], [x2,y2] ]
def angle_between(line1, line2):
    line1_rad = atan2(line1[1][y_coord] - line1[0][y_coord], line1[1][x_coord] - line1[0][x_coord])
    line2_rad = atan2(line2[1][y_coord] - line2[0][y_coord], line2[1][x_coord] - line2[0][x_coord])
    diff = line1_rad - line2_rad
    if diff < 0:
        diff += pi * 2

    # radians to degrees
    diff = degrees(diff)

    return diff

def to_first_quad(angle):
    return 360 - angle if angle > 180 else angle

def line_from(start_pos, end_pos):
    return [start_pos, end_pos]

def nth_waypoint_after(index, wpts, n):
    return (index + n) % len(wpts)

def reward_function(params):
    waypoints = params['waypoints']
    closest_waypoints_indices = params['closest_waypoints']
    heading = params['heading']
    current_pos = [params['x'], params['y']]
    steps = params['steps']
    progress = params['progress']
    speed = params['speed']
    is_left_of_center = params['is_left_of_center']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']

    # max reward possible
    reward = progress / steps * 10

    next_point_index = closest_waypoints_indices[1]
    behind_point_index = closest_waypoints_indices[0]

    next_point_pos = waypoints[next_point_index]
    behind_point_pos = waypoints[behind_point_index]

    # look ahead to the following waypoints
    near_point_index = nth_waypoint_after(next_point_index, waypoints, 2)
    far_point_index = nth_waypoint_after(near_point_index, waypoints, 3)
    really_far_point_index = nth_waypoint_after(near_point_index, waypoints, 5)
    near_point_pos = waypoints[near_point_index]
    far_point_pos = waypoints[far_point_index]
    really_far_point_pos = waypoints[ really_far_point_index ]

    # Calculate the direction in radians, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = atan2(next_point_pos[y_coord] - behind_point_pos[y_coord],
                                 next_point_pos[x_coord] - behind_point_pos[x_coord])

    # Convert to degrees
    track_direction = degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = to_first_quad( abs(track_direction - heading) )

    # In general it is best for the car to be aligned with the track when it is close to the center
    if distance_from_center < 0.2 * track_width:
        print("applying direction_diff penalty: {:f}".format(direction_diff), file=stderr)
        reward *= (1 - direction_diff / 360)

    # work out what the curve looks like ahead of us
    really_far_curve_angle = angle_between(line_from(really_far_point_pos, far_point_pos),
                                line_from(next_point_pos, behind_point_pos))
    far_curve_angle = angle_between(line_from(far_point_pos, near_point_pos),
                                line_from(next_point_pos, behind_point_pos))
    near_curve_angle = angle_between(line_from(near_point_pos, next_point_pos),
                                line_from(next_point_pos, behind_point_pos))

    curve_angle = max(to_first_quad(far_curve_angle), to_first_quad(near_curve_angle))

    if direction_diff < 20:
        print("really_far_curve: {:f}".format(really_far_curve_angle), file=stderr)
        print("far_curve: {:f}".format(far_curve_angle), file=stderr)
        print("near_curve: {:f}".format(near_curve_angle), file=stderr)

        # we may use this later to improve the position of the car w/ respect to the centre line to improve turning
        really_far_angle_diff = really_far_curve_angle - far_curve_angle
        print("really_far_angle_diff: {:f}".format(really_far_angle_diff), file=stderr)
        far_angle_diff = far_curve_angle - near_curve_angle
        print("far_angle_diff: {:f}".format(far_angle_diff), file=stderr)

        left_turn_coming = really_far_angle_diff > 5
        right_turn_coming = really_far_angle_diff < -5

        if left_turn_coming:
            print("TURN LEFT", file=stderr)
        if right_turn_coming:
            print("TURN RIGHT", file=stderr)

        left_reward_multiplier = 0.01 if left_turn_coming else 1.0
        right_reward_multiplier = 0.01 if right_turn_coming else 1.0

        # if we're clearly on one side pull the car to the correct one for coming turn via a penalty
        if abs(distance_from_center) > (0.1 * track_width):
            if is_left_of_center:
                reward *= left_reward_multiplier
                print("apply left_reward_multiplier: {:f}".format(left_reward_multiplier), file=stderr)
            else:
                reward *= right_reward_multiplier
                print("apply right_reward_multiplier: {:f}".format(right_reward_multiplier), file=stderr)
    
    # schumacher mode on
    safe_max_speed = max_speed

    if to_first_quad(far_curve_angle) > 0:
        safe_max_speed = max_speed / 3

    print("safe max speed: {:f} speed: {:f}".format(safe_max_speed, speed), file=stderr)

    if speed > safe_max_speed:
        speed_penalty = 0.1  # very likely to crash in the next couple of steps so penalize a lot
    else:
        if curve_angle < 6:
            if speed > max_speed / 3:
                # clearly we need to be going as fast as possible, so we give extra incentive (not a penalty in this case)
                speed_penalty = 1.0 + speed / max_speed
            else:
                speed_penalty = -0.1
        else:
            speed_penalty = 1.0

    print("speed_penalty: {:f}".format(speed_penalty), file=stderr)

    reward *= speed_penalty

    return float(reward)
