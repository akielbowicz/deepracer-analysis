from math import exp,sqrt, atan2, degrees, pi
import inspect

class RewardBase:
    max_progress = 100.0
    max_speed = 4.0
    SPEED_THRESHOLD = 2.7
    MAX_STEERING = 30.0
    
    def __init__(self, params):
        self._params = params
        self._set_attributes()
        self._log()
    
    def _set_attributes(self):
        for parameter,value in self._params.items():
            setattr(self, parameter, value)
        
    def __float__(self):
        return float(self._calculateReward())
        
    def _calculateReward(self):
        return self.penalize_steps()  
        
    def penalize_steps(self):
        return -1e-3
        
    def base_reward(self):
        return 1e-3
    
    def _log(self):
        print(self)
        
    def __str__(self):
        return f'REWARD_TRACE_LOG:[{self._methods()},{self._params}]'
        
    def _methods(self):
        return {d: getattr(self,d)() for d in dir(self) if inspect.ismethod( getattr(self,d) ) and not d.startswith("_") }
    
class Reward(RewardBase):
    
    def _calculateReward(self):
        return self.is_on_track() * self.speed_lock()

    def motion_reward(self):
        return ( self.base_reward()
                + self.penalize_steps() 
                + self.follow_the_center_line() ) 
                
    def follow_the_center_line(self):
        return exp(-2*self.distance_from_center**2/self.track_width**2)
        
    def is_on_track(self):
        return exp( self.motion_reward() 
                + self.progress_reward() 
                + self.advance_reward() 
                + self.control_steering()
                + self.direction_penalization() )/ (self.steps + 1) if self.all_wheels_on_track else -0.1

    def speed_lock(self):
        return 1.0 if self.speed <= self.SPEED_THRESHOLD else 1e-4
        
    def progress_reward(self):
        return  sqrt(self.progress/100) if int(self.progress) % 10 == 0 else 0.0
    
    def advance_reward(self):
        return 1/(self.steps+1) if int(self.progress) % 20 == 0 else 0.0 
        
    def control_steering(self):
        return 0.1*(-(self.steering_angle/self.MAX_STEERING)**2 + 2 )
    
        # Calculate the direction of the center line based on the closest waypoints
    def near_waypoints(self):
        next_point = self.waypoints[self.closest_waypoints[1]]
        prev_point = self.waypoints[self.closest_waypoints[0]]
        return next_point, prev_point

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    def track_direction(self):
        next_point,prev_point =  self.near_waypoints()
        track_direction = atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]) 
        # Convert to degree
        track_direction = degrees(track_direction)
        return track_direction
    
    def direction_diff(self):
        direction_diff = abs(self.track_direction() - self.heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        return direction_diff
    
    def direction_penalization(self):
        direction_diff = self.direction_diff()
        DIRECTION_THRESHOLD = 20.0
        return -0.5 - (direction_diff / 100.0) if direction_diff > DIRECTION_THRESHOLD else 0.0
            

def reward_function(params):
    return float(Reward(params))