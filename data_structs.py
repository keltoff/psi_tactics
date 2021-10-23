from copy import copy

class FeatureDictionary(dict):
    def update(self, other=None, **kwargs):
        if other is None:
            other = {}
        other.update(kwargs)

        for key, value in other.items():
            if isinstance(value, bool):
                self[key] = self[key] or value
            elif isinstance(value, int):
                self[key] = value + self[key]
            else:
                self[key] = value

    def __getitem__(self, item):
        if not item in self:
            return 0
        else:
            return dict.__getitem__(self, item)

    def __add__(self, other):
        result = copy(self)
        result.update(other)
        return result


if __name__ == '__main__':
    a = FeatureDictionary(x=5, ok=False)
    b = {'x': 2, 'y': 3, 'ok':True}
    c = {'ok': False}

    print(a + b + c)