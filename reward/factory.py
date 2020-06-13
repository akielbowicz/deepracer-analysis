class RewardFactory:

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
