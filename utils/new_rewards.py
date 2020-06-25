import numpy
def calculate_new_reward(reward_calculator, df, center_line, df_to_params, reward_name='new_reward' ):
    ''' update the dataframe with a given reward function using vectorized version  '''
    def f(row):
        return float(reward_calculator(df_to_params(row, center_line)))
    df[reward_name] = df.apply(f,axis=1)
    return df

def calculate_cumulative_reward(df, reward_column_names, use_stream=False):
    groupby_cols = ['iteration','episode'] + ( ['stream'] if use_stream else [] )
    cumulative_reward = df.sort_values('step').loc[:,groupby_cols + reward_column_names ].groupby(groupby_cols).cumsum()
    cumulative_reward.columns = [f'cumulative_{x}' for x in cumulative_reward.columns]
    return df.merge( cumulative_reward, left_index=True,right_index=True )

def summary(df,reward_names,use_stream=False, aditional_maps=None):
    aggregation_map = {'step':numpy.max,
                       'closest_waypoint_index': lambda x: x.values[0],
                       'progress':numpy.max,
                       'speed':numpy.mean,
                       'time':numpy.ptp,
                       'reward': numpy.sum,
                       'duration':numpy.max,
                      }
    aggregation_map.update({name : numpy.sum for name in reward_names })
    if aditional_maps: aggregation_map.update(aditional_maps)
    groupby_cols =  ( ['stream'] if use_stream else [] ) + ['iteration','episode'] 
    return df.groupby(groupby_cols).agg(aggregation_map)

def aggregate_episode_reward(df, reward_calculator, df_to_params, track, reward_name='new_reward'):
    '''  df should contain only episode information '''
    df = calculate_new_reward(reward_calculator, df, track.center_line, df_to_params, reward_name)
    return calculate_cumulative_reward( df,['reward',reward_name])    