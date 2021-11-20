import animations as ani
from tile_map.geometry.topology import *
from collections import namedtuple


Environment = namedtuple('Environment', 'map characters')


class AI:
    def __init__(self, npc):
        self.npc = npc

    def take_turn(self, gui, environment: Environment):
        pass

    def reaction(self, event):
        pass


class Spin(AI):
    def take_turn(self, gui, environment: Environment):
        gui.play_animation(ani.ScriptSpin(self.npc))


class TrackTarget(AI):
    def __init__(self, npc):
        super().__init__(npc)

        self.target = None
        self.aim = 0

    def take_turn(self, gui, environment: Environment):
        if self.target is None:
            self.target = self.closest_visible(environment.map, environment.characters.pcs)
            if self.target is not None:
                gui.play_animation(ani.ScriptAim(self.npc, self.target))

        if self.target is not None:
            los, difficulty = self.trace_shot(environment.map, self.target.pos)
            if not los:
                self.target = None
                self.aim = 0
                self.update_banner(None)
                self.npc.sprite.set_mode('stand')
            else:
                self.aim += 1
                self.update_banner(difficulty - self.aim)
                if self.aim >= difficulty:
                    # do shot
                    effect = None  # TODO perform attack
                    gui.play_animation(ani.ScriptAttack(self.npc, self.target, effect))

                    self.target = None
                    self.aim = 0
                    self.update_banner(None)

    def reaction(self, event):
        if event.is_a('player_move') and self.target is not None:
            self.npc.pos.dir = Flat4.dir_to(self.npc.pos, self.target.pos)

    def update_banner(self, eta):
        if self.target is None or eta is None:
            self.npc.banner = None
        else:
            self.npc.banner = 'countdown', eta

    def closest_visible(self, map_data, pcs):
        visible = [pc for pc in pcs if self.trace_shot(map_data, pc.pos)[0]]
        by_distance = sorted(visible, key=lambda pc: Flat4.distance(self.npc.pos, pc.pos))
        return next(iter(by_distance), None)

    def trace_shot(self, map_data, target_pos):
        path = Flat4.trace_shot(self.npc.pos, target_pos)
        for pos in path[:-1]:
            if not map_data.is_clear(pos):
                return False, None
        return True, 2
