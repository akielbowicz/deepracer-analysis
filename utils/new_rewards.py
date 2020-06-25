import numpy
import seaborn

def calculate_new_reward(reward_calculator, df, center_line, df_to_params, new_reward_name='new_reward' ):
    ''' update the dataframe with a given reward function using vectorized version
        reward_calculator should be a callable that recieves a params dictionary and returns an object castable to float
        df_to_params is a helper function that takes a series and transforms it into a dictionary of parameters
        new_reward_name is the column name of the new reward
    '''
    def f(row):
        return float(reward_calculator(df_to_params(row, center_line)))
    df[new_reward_name] = df.apply(f,axis=1)
    return df

def calculate_cumulative_reward(df, reward_column_names, use_stream=False):
    ''' Given a dataframe with instantaneous rewards aggregate it by 'iteration' and 'episode'
    returns a new dataframe with aditional columns named as cumulative_{x} where x is each element of reward_column_names
    reward_column_names: a list with the column names of the rewards
    '''
    groupby_cols = ['iteration','episode'] + ( ['stream'] if use_stream else [] )
    cumulative_reward = df.sort_values('step').loc[:,groupby_cols + reward_column_names ].groupby(groupby_cols).cumsum()
    cumulative_reward.columns = [f'cumulative_{x}' for x in cumulative_reward.columns]
    return df.merge( cumulative_reward, left_index=True,right_index=True )

def summary(df, reward_names,use_stream=False, aditional_maps=None):
    ''' aggregation of reward_names and some useful columns over 'iteration' and 'episode' 
    '''
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

def aggregate_episode_reward(df, reward_calculator, df_to_params, track, new_reward_name='new_reward'):
    '''  
    !!! df should contain only one episode information
    reward_calculator should be a callable that recieves a params dictionary and returns an object castable to float
    df_to_params is a helper function that takes a series and transforms it into a dictionary of parameters
    '''
    df = calculate_new_reward(reward_calculator, df, track.center_line, df_to_params, new_reward_name)
    return calculate_cumulative_reward( df,['reward',new_reward_name])    

def plot_new_reward(df,cols_to_plot):
    new_df = df.loc[:,['step'] + cols_to_plot ]
    new_df = new_df.set_index('step').sort_index()
    seaborn.lineplot(data=new_df,)