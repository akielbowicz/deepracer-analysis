from math import exp

class RewardBase:
    max_progress = 100.0 # per doc
    max_speed    = 1.0
    max_steering = 15.0

    def __init__(self, params):
        self._params = params
        self._set_attributes()

    def _set_attributes(self):
        for parameter,value in self._params.items():
            setattr(self, parameter, value)

    def __float__(self):
        return float(self._calculateReward())

    def optimal_steps(self):
        return self.track_length / self.max_speed * 15 #15 steps per second as camera has 15 frames per second

    def _calculateReward(self):
        return self.base_reward()  

    def base_reward(self):
        return 1e-3


class Reward(RewardBase):

    def _calculateReward(self):
        return ( self.base_reward()
                + self._motion_reward()
                + self.complete_track() )

    def _motion_reward(self):
        return ( self.stay_in_the_center()
                    * self.penalize_slow_movement()
                    * self.penalize_over_steering()
                    * self.kill_reward_when_off_track() 
                )
                
    def kill_reward_when_off_track(self):
        return 1.0 if self.all_wheels_on_track else 0.0

    def stay_in_the_center(self):
        return 1.0 if (0.5*self.track_width - self.distance_from_center) >= 0.05 else 0.0
        
    def complete_track(self):
        return (self.optimal_steps() / self.steps * 100) if self.progress == self.max_progress else 0.0 

    def penalize_slow_movement(self):
        return 0.8 if self.speed < self.max_speed else 1.0

    def penalize_over_steering(self):
        return 0.8 if abs(self.steering_angle) > self.max_steering else 1


def reward_function(params):
    return float(Reward(params))