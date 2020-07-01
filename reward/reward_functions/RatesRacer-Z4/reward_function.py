from math import exp

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
        
    def penalize_steps(self):
        return -1.0
        
class Reward(RewardBase):
    
    def _calculateReward(self):
        return ( self.penalize_steps() 
                + self.keep_on_track()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus() )
                
    def follow_the_center_line(self):
        return exp(-2*self.distance_from_center**2/self.track_width)
        
    def keep_on_track(self):
        return 1 if self.all_wheels_on_track else -100 
        
    def progress_bonus(self):
        return exp( self.progress - self.max_progress  )

    def speed_bonus(self):
        return exp( self.speed - self.max_speed )

def reward_function(params):
    return float(Reward(params))