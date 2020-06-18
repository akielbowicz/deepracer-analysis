import pandas 

def load_logs(file_name):
    sim_trace_log_column_names = ['episode', 'step', 'x-coordinate', 'y-coordinate', 'heading', 'steering_angle',       'speed', 'action_taken', 'reward', 'job_completed', 'all_wheels_on_track', 'progress','closest_waypoint_index', 'track_length', 'time','status']
    
    numeric_cols = ['episode', 'step', 'x-coordinate', 'y-coordinate', 'heading',
       'steering_angle', 'speed', 'action_taken', 'reward',  'progress', 'closest_waypoint_index',
       'track_length',]
    
    bool_cols = ['job_completed', 'all_wheels_on_track']
    
    df = pandas.read_csv(file_name,sep=',')
    df = df['@message'].str.split(',',expand=True)
    df.columns=sim_trace_log_column_names
    df['episode'] = df['episode'].str.replace('SIM_TRACE_LOG:','')
    df[numeric_cols] = df[numeric_cols].apply(pandas.to_numeric)
    
    df[bool_cols] = df[bool_cols].applymap(lambda x: {'True':True,'False':False}.get(x))
    df['numeric_timestamp'] = df['time'].apply(float)
    df['time'] = df['time'].apply(lambda x: pandas.Timestamp(int(float(x)),unit='s'))
    df['status']  = df['status'].astype('category')
    
    return df

def df_to_params_orig(df_row, waypoints):
        """Convert log data to parameters to be passed to be passed to the reward function

        Arguments:
        df_row - single row to be converted to parameters
        waypoints - waypoints to put into the parameters

        Returns:
        A dictionary of parameters
        """
        from deepracer.tracks import GeometryUtils as gu
        import numpy as np
        waypoint = df_row['closest_waypoint']
        before = waypoint - 1
        if waypoints[waypoint].tolist() == waypoints[before].tolist():
            before -= 1
        after = (waypoint + 1) % len(waypoints)

        if waypoints[waypoint].tolist() == waypoints[after].tolist():
            after = (after + 1) % len(waypoints)

        current_location = np.array([df_row['x'], df_row['y']])

        print(  waypoints[waypoint],
                waypoints[after],
                [df_row['x'], df_row['y']] )
        
        closest_point = gu.get_a_point_on_a_line_closest_to_point(
            waypoints[before],
            waypoints[waypoint],
            [df_row['x'], df_row['y']]
        )


        if gu.is_point_roughly_on_the_line(
            waypoints[before],
            waypoints[waypoint],
            closest_point[0], closest_point[1]
        ):
            closest_waypoints = [before, waypoint]
        else:
            closest_waypoints = [waypoint, after]
            closest_point = gu.get_a_point_on_a_line_closest_to_point(
                waypoints[waypoint],
                waypoints[after],
                [df_row['x'], df_row['y']]
            )

        params = {
            'x': df_row['x'],
            'y': df_row['y'],
            'speed': df_row['throttle'],
            'steps': df_row['steps'],
            'progress': df_row['progress'],
            'heading': df_row['yaw'] * 180 / 3.14,
            'closest_waypoints': closest_waypoints,
            'steering_angle': df_row['steer'] * 180 / 3.14,
            'waypoints': waypoints,
            'distance_from_center':
                gu.get_vector_length(
                    (
                        closest_point -
                        current_location
                    )),
            'timestamp': df_row['timestamp'],
            # TODO I didn't need them yet. DOIT
            'track_width': 0.60,
            'is_left_of_center': None,
            'all_wheels_on_track': True,
            'is_reversed': False,
        }

        return params
    
def load_sample_complete_laps(path):
    sample_laps = ( pandas.read_csv(path)
                          .groupby('stream')
                          .agg(list)['episode'] )
    DFs = []
    for filename, episodes in sample_laps.iteritems():
        df = load_logs(f'../logs/{filename}')
        df = df[df['episode'].isin(episodes)]
        df['stream'] = filename
#         df['name'] = [f'{filename}_{ep}' for ep in episodes]
        DFs.append(df)
    df = pandas.concat(DFs).reset_index()
#     df['stream'] = df['stream'].astype('category')
    return df