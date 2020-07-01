from math import exp, pow, pi, cos

class RewardBase:
    max_progress = 100.0 # per doc
    max_speed    = 3
    max_steering = 20.0
    complete_reward_frequency = 10 # we give out reward every this many steps only

    def __init__(self, params):
        self._params = params
        self._set_attributes()
        print(params)
        
    def _set_attributes(self):
        for parameter,value in self._params.items():
            setattr(self, parameter, value)

    def __float__(self):
        return float(self._calculateReward())

    def _calculateReward(self):
        return self.base_reward()  

    def base_reward(self):
        return -0.1


class Reward(RewardBase):

    def _calculateReward(self):
        reward_when_alive = self.kill_reward_when_off_track() * (self._motion_reward() + self.complete_track())
        
        return self.base_reward() + reward_when_alive

    def _motion_reward(self):
        return ( self.stay_in_the_center()
                    * self.penalize_slow_movement()
                    * self.penalize_over_steering()
                    )
                
    def kill_reward_when_off_track(self):
        return 1.0 if self.all_wheels_on_track else 0.0

    def stay_in_the_center(self):
        return exp(-2*self.distance_from_center**2/self.track_width)
        
    def complete_track(self):
        return self.progress**2 if int(self.progress) % 10 == 0 else 0.0

    def penalize_slow_movement(self):
        
        if self.speed == self.max_speed:
            return 1.5
            
        if self.speed >= self.max_speed * 0.8:
            return 2.0
            
        if self.speed >= self.max_speed * 0.6:
            return 0.6
        
        return 0.5

    def penalize_over_steering(self):
        return cos(pi*self.steering_angle/180)


def reward_function(params):
    return float(Reward(params))