from traitlets import CFloat,List,Int,CBool, observe, HasTraits,All


class Parameters(HasTraits):

    all_wheels_on_track =  CBool(True ).tag(sync=True)#s.all_wheels_on_track,
    x =  CFloat(0.0).tag(sync=True) #s['x-coordinate'],
    y =  CFloat(0.0).tag(sync=True) #s['y-coordinate'],
    closest_objects =  List([]).tag(sync=True) #
    closest_waypoints = List([]).tag(sync=True)  #old_params['closest_waypoints'],#[int, int], π indices of the two nearest waypoints.
    distance_from_center = CFloat(0.0).tag(sync=True) #0.0,#float, π distance in meters from the track center
    is_crashed =  CBool(False, help="").tag(sync=True)
    is_left_of_center = CBool(False, help="").tag(sync=True)
    is_offtrack = CBool(False, help="").tag(sync=True) #s.status == 'off_track'
    is_reversed = CBool(False, help="").tag(sync=True)
    heading = CFloat(0.0).tag(sync=True) #s.heading,
    objects_distance =  List([]).tag(sync=True) #[ ],
    objects_heading =  List([]).tag(sync=True) #[ ],
    objects_left_of_center =List([]).tag(sync=True) #  [ ],
    objects_location =  List([]).tag(sync=True) #[],
    objects_speed= List([]).tag(sync=True) #[ ],
    progress = CFloat(0.0).tag(sync=True) #s.progress,
    speed = CFloat(0.0).tag(sync=True) #s.speed,
    steering_angle = CFloat(0.0).tag(sync=True) # s.step,.steering_angle,
    steps =  Int(0).tag(sync=True) #s.step,
    track_length = CFloat(17.6, help='Length in meters').tag(sync=True)
    track_width = CFloat(0.76).tag(sync=True)
    waypoints =  List([]).tag(sync=True) #center_line

    def __init__(self, params=None, **kwargs):
        if params:
            self._load_params(params)
        super().__init__(**kwargs)
        observe(self.on_change,names=All)

    def _load_params(self, params):
        for key, value in params.items():
           print(key,value)
          # attr = getattr(self,key)
          # print('attr: ',attr)
          # attr = value

    @staticmethod
    def on_change(change):
        print(change)
