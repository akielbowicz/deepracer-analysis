from math import exp

def reward_function(params):
    '''
    Example of rewarding the agent to stay inside the two borders of the track
    '''
    
    # Read input parameters
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    speed = params['speed']
    progress = params['progress']
    
    # Give a very low reward by default
    reward = 1e-3
    
    # no speed bonus by default
    speedbonus = 0
    
    # no progress bonus by default
    progressbonus = 0

    # Give a high reward if no wheels go off the track and
    # the agent is somewhere in between the track borders
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward = 1.0

    # give exponentially increasing bonus but keep it in the range 0 -> 1.0
    maxspeed = 1.0 # per standard deepRacer specs
    speedbonus = exp(speed) / exp(maxspeed)
    
    # give exponentially increasing bonus but keep it in the range 0 -> 1.0
    maxprogress = 100.0 # per doc
    progressbonus = exp(progress) / exp(maxprogress)

    reward = reward + speedbonus + progressbonus
    
    # Always return a float value
    return float(reward)