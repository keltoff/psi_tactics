from enum import Enum, auto
from collections import namedtuple
import battle_logic as bl
from map_gui import MapGui, Event

class MapScreen:
    def __init__(self, game_window):
        self.gui = MapGui(game_window)

    def perform_battle(self, characters, scenario):

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
        pass

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
                    new_pos = action.pos
                    new_pos.dir = action.player.pos.dir
                    action.player.pos = new_pos  # action.pos
                    print('Moved to: ', action.player.pos)
                    action.player.moved = True
                else:
                    record('Illegal move', action)
            elif action.is_a(MapGui.EV_ATTACK):
                if bl.check_attack_legal(action):
                    shooter = action.player
                    target = action.target

                    effect = bl.process_attack(shooter, target)

                    self.gui.play_animation('Attack', shooter, target, effect)

                    bl.apply_attack(effect, shooter, target)
                else:
                    record('Illegal attack', action)
            elif action.is_a('quit'):
                done = True
                return done


            elif action.is_a(MapGui.EV_TURN_END):
                self.display_banner('Turn end')

                # refresh characters
                for char in characters:
                    char.moved = False
                    char.acted = False

                break

        done = False  # do not trigger a game end
        return done

    def handle_opfor_turn(self, npcs):
        self.display_banner('Opfor Turn')

        for npc in npcs:
            if npc.visible:
                self.gui.focus(npc)
                self.gui.play_animation('Emote', npc, 'Spin')

        done = False
        return done


def record(text, action):
    print(text, repr(action))


if __name__ == '__main__':
    # create the screen gui

    # create charaters and npcs
    # in normal game, these would be loaded
    characters = []

    Scenario = namedtuple('Scenario', 'setup map npcs')
    setup = None
    map = None
    npcs = []
    scenario = Scenario(setup, map, npcs)

    # TODO move to main_loop
    import pygame
    pygame.init()
    window = pygame.display.set_mode((800, 700))

    screen = MapScreen(window)
    screen.perform_battle(characters, scenario)