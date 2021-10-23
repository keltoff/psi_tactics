from data_structs import FeatureDictionary

class Item:
    def __init__(self, name, weight=0, mods={}, action=None, **action_params):
        self.name = name
        self.weight = weight
        self.mods = mods

        self.action = action
        self.action_params = action_params

    def __str__(self):
        return self.name


def build_item_list():
    return [Item('Stunner', action='shoot', allow=True),
            Item('Grenade', action='grenade', allow=True, uses=2),
            Item('Toolkit', action='fix', allow=True),
            Item('Shield', mods={'Shield': 1}),
            Item('Smokebomb', action='smoke', allow=True, uses=3),
            ]


class Action:
    def __init__(self, key, name, **stats):
        self.key = key
        self.name = name
        self.stats = FeatureDictionary(stats)

    @property
    def allow(self):
        return self.stats.get('allow', False)

    @property
    def stats_display(self):
        return {k: self.stats[k] for k in self.stats if k != 'allow'}

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.key == self.key

    def __hash__(self):
        return hash(self.key)

    def __getitem__(self, item):
        return self.stats[item]


def build_action_list():
    return [Action('shoot', 'Shoot', allow=True),
            Action('grenade', 'Toss grenade', uses=0, damage=1),
            Action('fix', 'Hack/Fix'),
            Action('smoke', 'Vanish', ninja='only'),
            ]