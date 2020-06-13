from factory import RewardFactory
from awsreward import AWSReward

import unittest

class StubBase:
    def __init__(self,params):
        pass

class StubA(StubBase):
    pass

class StubB(StubBase):
    pass

class StubC(StubA):
    pass

PARAMS = {
    "all_wheels_on_track": True,        # flag to indicate if the agent is on the track
    "x": 1.0,                            # agent's x-coordinate in meters
    "y": 1.0,                            # agent's y-coordinate in meters
    "closest_objects": [1, 1],         # zero-based indices of the two closest objects to the agent's current position of (x, y).
    "closest_waypoints": [1, 1],       # indices of the two nearest waypoints.
    "distance_from_center": 1.0,         # distance in meters from the track center
    "is_crashed": True,                 # Boolean flag to indicate whether the agent has crashed.
    "is_left_of_center": True,          # Flag to indicate if the agent is on the left side to the track center or not.
    "is_offtrack": True,                # Boolean flag to indicate whether the agent has gone off track.
    "is_reversed": True,                # flag to indicate if the agent is driving clockwise (True) or counter clockwise (False).
    "heading": 1.0,                      # agent's yaw in degrees
    "objects_distance": [1.0, ],         # list of the objects' distances in meters between 0 and track_length in relation to the starting line.
    "objects_heading": [1.0, ],          # list of the objects' headings in degrees between -180 and 180.
    "objects_left_of_center": [True, ], # list of Boolean flags indicating whether elements' objects are left of the center (True) or not (False).
    "objects_location": [(1.0, 1.0),], # list of object locations [(x,y), ...].
    "objects_speed": [1.0, ],            # list of the objects' speeds in meters per second.
    "progress": 1.0,                     # percentage of track completed
    "speed": 1.0,                        # agent's speed in meters per second (m/s)
    "steering_angle": 1.0,               # agent's steering angle in degrees
    "steps": 1,                          # number steps completed
    "track_length": 1.0,                 # track length in meters.
    "track_width": 1.0,                  # width of the track
    "waypoints": [(1.0, 1.0), ]        # list of (x,y) as milestones along the track center

}

class FactoryTest(unittest.TestCase):

    def test_all_subclasses_are_generated(self):
        self.assertCountEqual(list(RewardFactory.subclasses(StubBase)), [StubA, StubB, StubC])

    def test_factory_instanciates_correct_class(self):
        factory = RewardFactory(StubBase)
        stub = factory.build('StubC',{})
        self.assertIsInstance(stub, StubC)

class RewardsTest(unittest.TestCase):

    def test_all_awsrewards_can_be_casted_to_floats(self):
        factory = RewardFactory(AWSReward)
        params = {}
        for reward_name in factory.rewards():
            self.assertIsNotNone(float(factory.build(reward_name, PARAMS)))
