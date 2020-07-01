from math import exp, pow

class RewardBase:
    max_progress = 100.0 # per doc
    max_speed    = 3
    max_steering = 20.0
    complete_reward_frequency = 10 # we give out reward every this many steps only

    def __init__(self, params):
        self._params = params
        self._set_attributes()

    def _set_attributes(self):
        for parameter,value in self._params.items():
            setattr(self, parameter, value)

    def __float__(self):
        return float(self._calculateReward())

    # optimal steps proportional to the progress so far (there is an assumption on even distribution of steps across the track
    def optimal_steps(self):
        # make the optimal number of steps 20% more conservative than what we calculate based on length
        optimal_error = 1.50
        
        #15 steps per second as camera has 15 frames per second
        return self.progress / 100 * optimal_error * self.track_length / self.max_speed * 15 

    def _calculateReward(self):
        return self.base_reward()  

    def base_reward(self):
        return 1e-3


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
        return 1.0 if (0.5*self.track_width - self.distance_from_center) >= 0.05 else 0.0
        
    def complete_track(self):
        # we only give out reward every 10 steps
        if (self.steps % self.complete_reward_frequency) != 0:
            return 0.0
        
        step_diff = self.steps - self.optimal_steps()
        
        step_reward_ratio = self.optimal_steps() / step_diff
        
        return step_reward_ratio * self.complete_reward_frequency

    def penalize_slow_movement(self):
        
        if self.speed == self.max_speed:
            return 1.0
            
        if self.speed >= self.max_speed * 0.8:
            return 0.9
            
        if self.speed >= self.max_speed * 0.6:
            return 0.8
        
        return 0.5

    def penalize_over_steering(self):
        # soften penalty if we're going slowly as this is what will be needed on some of the turns
        steering_penalty = 0.20 * self.speed / self.max_speed 
        
        return (1.0 - steering_penalty) if abs(self.steering_angle) > self.max_steering else 1.0


def reward_function(params):
    return float(Reward(params))