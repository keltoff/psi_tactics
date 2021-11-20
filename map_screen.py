from enum import Enum, auto
from collections import namedtuple
import battle_logic as bl
from map_gui import MapGui, Event
from animations import ScriptWalk, ScriptAttack, ScriptSpin
from tile_map.data_types.position import Position as Pos
from dataclasses import dataclass
import npc_ai
from character import Character, Role
from tile_map.graphics.storage import Storage


class MapScreen:
    def __init__(self, game_window, map_file):
        self.gui = MapGui(game_window, map_file)

    def perform_battle(self, characters, scenario):

        # init
        self.gui.load_sprites_in_map(characters, scenario.npcs, scenario.objects)

        self.display_intro(scenario)

        # Main game loop

        while True:
            done = self.handle_player_turn(characters)
            if done:
                break

            done = self.handle_opfor_turn(scenario.npcs)
            if done:
                break

            # done = self.handle_independent_effects()
            # if done:
            #     break

        results = self.evaluate_status()
        self.display_outro(scenario, results)

        return results

    def display_intro(self, scenario):
        pass

    def display_outro(self, scenario, results):
        pass

    def display_banner(self, text):
        print(text)

    def evaluate_status(self):
        results = []
        return results

    def handle_player_turn(self, characters):

        # Let player play as many moves as he want / can
        while True:
            action = self.gui.get_action()
            print(f'Action: {action}')
            if action.is_a(MapGui.EV_MOVE):
                if bl.check_move_legal(action):
                    self.gui.play_animation(ScriptWalk(action.player, action.path))

                    new_pos = action.pos
                    new_pos.dir = action.player.pos.dir
                    action.player.pos = new_pos  # action.pos
                    print('Moved to: ', action.player.pos)
                    action.player.moved = True
                else:
                    record('Illegal move', action)
            elif action.is_a(MapGui.EV_ATTACK):
                if bl.check_attack_legal(action):
                    shooter = action.shooter
                    target = action.target

                    effect = bl.process_attack(shooter.pawn, target.pawn)

                    self.gui.play_animation(ScriptAttack(shooter, target, effect))

                    bl.apply_attack(effect, shooter.pawn, target.pawn)
                else:
                    record('Illegal attack', action)
            elif action.is_a('quit'):
                done = True
                return done

            elif action.is_a(MapGui.EV_TURN_END):
                self.display_banner('Turn end')

                # refresh characters
                # for char in characters:
                #     char.moved = False
                #     char.acted = False

                break

        done = False  # do not trigger a game end
        return done

    def handle_opfor_turn(self, npcs):
        self.display_banner('Opfor Turn')

        env = npc_ai.Environment(self.gui.map, self.gui.char_display.characters)

        for npc in npcs:
            if True:  #npc.visible:
                self.gui.focus(npc)
                npc.ai.take_turn(self.gui, env)

        done = False
        return done


def record(text, action):
    print(text, repr(action))


@dataclass
class Char:
    img_key: str
    pos: Pos
    pawn: bl.Pawn
    sprite = None
    ai = None


if __name__ == '__main__':
    # create the screen gui

    # sprite_storage = Storage.load('data/graphics_iso.xml')
    store = Storage.load('data/sprites.xml')

    Scenario = namedtuple('Scenario', 'setup map npcs objects')

    # create charaters and npcs
    # in normal game, these would be loaded
    characters = [Character.build(name='Warrior', hp=10, focus=8, psi=2,
                                  sprite=store.make_sprite('war', Pos(13, 5, d=0)), role=Role.PC),
                  Character.build(name='Jennifer', hp=12, focus=5,
                                  sprite=store.make_sprite('jen', Pos(11, 4, d=1)), role=Role.PC)
                  ]

    objects = [Character.build(name='Box', hp=1, focus=0,
                               sprite=store.make_sprite('box', pos), role=Role.Object)
               for pos in [Pos(10, 4), Pos(12, 4), Pos(14, 4), Pos(10, 5), Pos(14, 5)]]

    npcs = [Character.build(name='Thug', hp=5, focus=2, ai_class=npc_ai.TrackTarget,
                            sprite=store.make_sprite('red', pos), role=Role.NPC)
            for pos in [Pos(9, 3, d=2),
                        Pos(15, 3, d=2),
                        Pos(8, 5, d=1),
                        Pos(16, 5, d=3)]]
    npcs.append(Character.build(name='Lenny', hp=5, focus=2, ai_class=npc_ai.Spin,
                                sprite=store.make_sprite('red', Pos(12, 3, d=2)), role=Role.NPC))

    scenario = Scenario(setup=None, map=None, npcs=npcs, objects=objects)

    # TODO move to main_loop
    import pygame
    pygame.init()
    window = pygame.display.set_mode((800, 700))

    # screen = MapScreen(window, map_file='data/mapdata.xml')
    screen = MapScreen(window, map_file='data/mapdata_flat.xml')
    screen.perform_battle(characters, scenario)
