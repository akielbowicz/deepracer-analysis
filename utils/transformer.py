from deepracer.logs import NewRewardUtils
import scipy.linalg 
import numpy

def df_to_params(s,center_line):
    
    old_params = NewRewardUtils.df_to_params(new_names(s), center_line)
    
    params = {
     "all_wheels_on_track": s.all_wheels_on_track,
     "x": s['x'],
     "y": s['y'],
     "closest_objects": [],
     "closest_waypoints": old_params['closest_waypoints'],#[int, int], π indices of the two nearest waypoints.
     "distance_from_center": old_params['distance_from_center'],#float, π distance in meters from the track center
     "is_crashed":False,
     "is_left_of_center": False,#Boolean, π Flag to indicate if the agent is on the leftside to the track center or not.
     "is_offtrack": s.status == 'off_track',
     "is_reversed": False,
     "heading": s.heading,
     "objects_distance": [ ],
     "objects_heading": [ ],
     "objects_left_of_center": [ ],
     "objects_location": [], "objects_speed": [ ],
     "progress": s.progress,
     "speed": s.speed,
     "steering_angle": s.steering_angle,
     "steps": s.step,
     "track_length": s.track_length,
     "track_width": 0.76,
     "waypoints": center_line,
}
    
    return params

def new_names(serie):
    new_names = {'step' :'steps',
                 'heading':'yaw',
                 'steering_angle':'steer',
                  'speed':'throttle',
                 'job_completed' : 'done',
                 'all_wheels_on_track':'on_track',
                'closest_waypoint_index':'closest_waypoint',
                 'track_length':'track_len', 
                 'time':'timestamp',
                }
    return serie.rename(new_names)

def new_names_df(df):
    new_names = {
                 'step' :'steps',
                 'heading':'yaw',
                 'steering_angle':'steer',
                 'speed':'throttle',
                 'job_completed' : 'done',
                 'all_wheels_on_track':'on_track',
                 'closest_waypoint_index':'closest_waypoint',
                 'track_length':'track_len', 
#                  'time':'timestamp',
                 'timestapm':'true_timestamp',
                 'numeric_timestamp':'timestamp'
                }
    return df.rename(columns=new_names)

def calculate_iteration(df):
    df['iteration']=df['episode'].apply( lambda x: int( x/ 20) + 1)
    
def calculate_velocity(df):
    "It should be calculated by episode or it will have strange values at the begining and  end"
    x, y, t = df[['x', 'y', 'numeric_timestamp']].values.T
    dx, dy, dt = numpy.diff([x, y, t],prepend=0)  
    df['velocity'] = scipy.linalg.norm([dx, dy], axis=0) / dt 
    return df
    
def calculate_duration(df):
    df['duration'] = df[['episode','numeric_timestamp']].groupby('episode').transform(lambda x: x - x.min())

def get_episode(df,episode):
    ep = df.loc[df.episode == episode, :].sort_values('step')
    ep = calculate_velocity(ep)
    return ep