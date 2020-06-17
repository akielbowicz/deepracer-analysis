class RewardFactory:
    DEFAULT_MISSING_PARAMETERS = {'track_width': 0.76, 'track_length': 17.67}

    def __init__(self, base_class):
        self._base_class = base_class
        self._classes = self._build_class_map()

    @staticmethod
    def subclasses(cls_):
        for subclass in cls_.__subclasses__():
            yield from RewardFactory.subclasses(subclass)
            yield subclass

    def _build_class_map(self):
        return { cls_.__name__ : cls_ for cls_ in self.subclasses(self._base_class) }

    def build(self, reward_name, params):
        cls_ = self._classes.get(reward_name, self._base_class)
        return cls_(params)

    def rewards(self):
        return [cls for cls in self._classes]

    def print_available_reward_classes(self):
        print(self.rewards())

    def calculate_new_reward(self, df, center_line, df_to_params, reward_name,missing_params=None):
        ''' update the dataframe with a given reward function '''
        def f(row):
            params = df_to_params(row, center_line)
            if missing_params:
                params.update(missing_params)
            rw = self.build(reward_name,params)
            return float(rw)

        df[reward_name] = df.apply(f,axis=1)

    def calculate_all_rewards(self,df,center_line,df_to_params,missing_params):
        ''' Updates the dataframe with all the available rewards '''
        names = self.rewards()
        def f(row,reward_names):
            params = df_to_params(row, center_line)
            if missing_params:
                params.update(missing_params)
            
            return [ float(self.build(reward_name,params)) for reward_name in reward_names ]

        df[names] = df.apply(f,axis=1,result_type='expand',**{'reward_names':names})

        