from tile_map.geometry.topology import *
from math import inf


class Script:
    def __init__(self):
        self.t = 0
        self.next_time = 0
        self.cursor = self.play_out()

    def update(self, time):
        self.t += time

        while self.t > self.next_time:
            self.t -= self.next_time
            self.next_time = next(self.cursor, inf)

    def done(self):
        return self.next_time is inf

    def play_out(self):
        # Override in children, DO NOT call this one
        # Use "yield time_in_ms" to wait that long
        raise StopIteration


class ScriptWalk(Script):
    def __init__(self, actor, path, **params):
        super().__init__()
        self.actor = actor
        self.path = path

    def play_out(self):
        self.actor.set_mode('walk')

        for pos in self.path:
            print(f'Moving to {pos}')
            self.actor.pos = pos
            yield 200

        self.actor.set_mode('stand')


class ScriptSpin(Script):
    def __init__(self, actor):
        super().__init__()
        self.actor = actor

    def play_out(self):
        self.actor.set_mode('spin')
        yield 1500
        self.actor.set_mode('stand')


class ScriptAttack(Script):
    def __init__(self, actor, target, effect):
        super().__init__()
        self.actor = actor
        self.target = target
        self.effect = effect

    def play_out(self):
        self.actor.pos.dir = Flat4.dir_to(self.actor.pos, self.target.pos)  # HACK: should not have to call it here
        self.actor.set_mode('aim')

        yield 500

        # TODO add_effect('Beam', self.actor, self.target)  # use effect too
        self.target.set_mode('is_hit')

        yield 500

        self.actor.set_mode('stand')
        self.target.set_mode('stand')
        # remove_effect ??


class ScriptAim(Script):
    def __init__(self, actor, target):
        super().__init__()
        self.actor = actor
        self.target = target

    def play_out(self):
        self.actor.pos.dir = Flat4.dir_to(self.actor.pos, self.target.pos)  # HACK: should not have to call it here
        self.actor.set_mode('aim')
        yield 500
