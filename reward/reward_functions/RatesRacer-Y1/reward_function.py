from math import exp, cos, pi

class RewardBase:
    max_progress = 100.0 # per doc
    max_speed = 1.0
    
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
        
    def base_reward(self):
        return 1e-3
        
class Reward(RewardBase):
    
    def _calculateReward(self):
        if self.all_wheels_on_track:
            return ( self.base_reward()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus()
                + self.control_steering() )
        else:
            return self.base_reward()
                
    def follow_the_center_line(self):
        return exp(-2*self.distance_from_center**2/self.track_width)
        
    def progress_bonus(self):
        return exp(self.progress / self.max_progress) / exp(1.0)

    def speed_bonus(self):
        return exp(self.speed) / exp (self.max_speed)
        
    def control_steering(self):
        return cos(pi*self.steering_angle/180)

def reward_function(params):
    return float(Reward(params))