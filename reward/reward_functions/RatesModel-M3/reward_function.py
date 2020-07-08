from math import exp,sqrt

class RewardBase:
    max_progress = 100.0
    max_speed = 4.0
    SPEED_THRESHOLD = 2.0
    MAX_STEERING = 30.0
    
    def __init__(self, params):
        self._params = params
        self._set_attributes()
    
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
        
class Reward(RewardBase):
    
    def _calculateReward(self):
        return self.is_on_track() * self.speed_lock()

    def motion_reward(self):
        return ( self.base_reward()
                + self.penalize_steps() 
                + self.follow_the_center_line() * self.control_steering() ) 
                
    def follow_the_center_line(self):
        return exp(-2*self.distance_from_center**2/self.track_width)
        
    def is_on_track(self):
        return self.motion_reward() + self.progress_reward() + self.advance_reward()  if self.all_wheels_on_track else -0.1

    def speed_lock(self):
        return 1.0 if self.speed <= self.SPEED_THRESHOLD else 1e-4
        
    def progress_reward(self):
        return  sqrt(self.progress/100) if int(self.progress) % 10 == 0 else 0.0
    
    def advance_reward(self):
        return 1/(self.steps+1) if int(self.progress) % 20 == 0 else 0.0 
        
    def control_steering(self):
        return 0.5*(-(self.steering_angle/self.MAX_STEERING)**2 + 2 )

def reward_function(params):
    return float(Reward(params))