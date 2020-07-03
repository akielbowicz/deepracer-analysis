from math import exp, sqrt

def reward_function(params):
    '''
    Example of rewarding the agent to follow center line
    '''
    
    # Read input parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    progress = params['progress']
    steps = params['steps'] + 1
    wheels_on_track = params['all_wheels_on_track']
    
    reward = 1.0
    # Calculate 3 markers that are at varying distances away from the center line
    reward *= exp(-distance_from_center**2) 
    
    progress_reward =  progress/100 if int(10*progress) % 100 == 0 else 0.0
    
    reward += progress_reward
    
    reward = reward if wheels_on_track else -0.01
    
    trace_log = f'"reward":{reward},"progress_reward":{progress_reward}'
    print(f'REWARD_TRACE_LOG:{trace_log}')
    return float(reward)