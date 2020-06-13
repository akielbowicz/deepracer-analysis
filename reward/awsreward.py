from math import exp, cos, pi

class BaseReward:
    max_progress = 100.0
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

    def _calculateReward(self):
        return self.base_reward()

    def base_reward(self):
        return 1e-3

class AWSReward(BaseReward):

    def optimal_steps(self):
        '''15 steps per second as camera has 15 frames per second'''
        return self.track_length / self.max_speed * 15.0

    def penalize_steps(self):
        return -1.0

    def speed_bonus(self):
        return exp(self.speed - self.max_speed)

    def stay_on_track(self):
        return  1.0 if self.all_wheels_on_track and self.is_on_track() else self.base_reward()

    def is_on_track(self):
        return (0.5*self.track_width - self.distance_from_center) >= 0.05

    def progress_bonus(self):
        return exp(self.progress - self.max_progress)

    def follow_the_center_line(self):
        return exp(-2.0*self.distance_from_center**2.0/self.track_width)

    def keep_on_track(self):
        return 1.0 if self.all_wheels_on_track else -100.0

    def control_steering(self):
        return cos(pi*self.steering_angle/180.0)


class RewardZ1(AWSReward):

    max_speed = 5.0  # per the deepracer documentation

    def _calculateReward(self):
        return self.stay_on_track() + self.speed_bonus()


class RewardZ2(RewardZ1):
    pass

class RewardZ3(RewardZ1):

    def _calculateReward(self):
        return ( self.stay_on_track()
                + self.speed_bonus()
                + self.progress_bonus() )


class RewardZ4(AWSReward):

    def _calculateReward(self):
        return ( self.penalize_steps()
                + self.keep_on_track()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus() )



class RewardZ4_2(AWSReward):

    def _calculateReward(self):
        return ( self.penalize_steps()
                + self.keep_on_track()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus()
                + self.control_steering() )


class RewardZ5(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward()
            + self.penalize_steps()
            + self.keep_on_track()
            + self.follow_the_center_line()
            + self.progress_bonus()
            + self.speed_bonus()
            + self.control_steering() )

class RewardZ6(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward()
                + self.penalize_steps()
                + self.keep_on_track()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus()
                + self.control_steering() )

    def keep_on_track(self):
        return 1 if self.all_wheels_on_track else -1


class RewardZ7(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward() if self.all_wheels_on_track else
                ( self.base_reward()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus()
                + self.control_steering() ) )

    def progress_bonus(self):
        return exp( self.progress / 100.0 - self.max_progress )


class RewardY1(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward() if self.all_wheels_on_track else
                ( self.base_reward()
                + self.follow_the_center_line()
                + self.progress_bonus()
                + self.speed_bonus()
                + self.control_steering() ) )

    def progress_bonus(self):
        return exp( self.progress / self.max_progress - 1.0)


class RewardY2(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward() if self.all_wheels_on_track else
                 ( self.base_reward()
                + (self.weight_center() * self.follow_the_center_line())
                + (self.weight_progress() * self.progress_bonus())
                + (self.weight_speed() * self.speed_bonus())
                + (self.weight_steering() * self.control_steering()) ) )

    def weight_steering(self):
        return 1.0

    def weight_center(self):
        return 3.0

    def weight_progress(self):
        return 4.0

    def weight_speed(self):
        return 2.0

    def progress_bonus(self):
        return exp(self.progress / self.max_progress - 1.0)


class RewardX1(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward()
            + self._motion_reward()
            + self.complete_track() )

    def _motion_reward(self):
        return ( self.stay_in_the_center()
            + self.penalize_slow_movement()
            * self.penalize_over_steering()
            * self.kill_reward_when_off_track())

    def kill_reward_when_off_track(self):
        return 1.0 if self.all_wheels_on_track else 0.0

    def stay_in_the_center(self):
        return 1.0 if self.is_on_track() else 0.0

    def complete_track(self):
        return 100.0 if self.progress == self.max_progress else 0.0

    def penalize_slow_movement(self):
        return 0.8 if self.speed < self.max_speed else 1.0

    def penalize_over_steering(self):
        return 0.8 if abs(self.steering_angle) > self.max_steering else 1.0


class RewardW2(AWSReward):

    def _calculateReward(self):
        return ( self.base_reward()
            + self._motion_reward()
            + self.complete_track() )

    def _motion_reward(self):
        return ( self.stay_in_the_center()
                * self.penalize_slow_movement()
                * self.penalize_over_steering()
                * self.kill_reward_when_off_track() )

    def kill_reward_when_off_track(self):
        return 1.0 if self.all_wheels_on_track else 0.0

    def stay_in_the_center(self):
        return 1.0 if self.is_on_track() else 0.0

    def complete_track(self):
        return (self.optimal_steps() / self.steps * 100) if self.progress == self.max_progress else 0.0

    def penalize_slow_movement(self):
        return 0.8 if self.speed < self.max_speed else 1.0

    def penalize_over_steering(self):
        return 0.8 if abs(self.steering_angle) > self.max_steering else 1.0
