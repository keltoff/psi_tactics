from enum import Enum, auto
from math import inf
import pygame
from collections import namedtuple
from widgets import Event, CharacterOrganizer, CharacterDisplay, KeyBinder, MapWrapper, TargetDisplay
from tile_map.map_display import Display
from tile_map.map_display import IsoSketch
from tile_map.map_storage.map_storage import MapSet
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.topology import *
from tile_map.gui import Gui
from animations import Script


class MapGuiEvents(Enum):
    PlayerMoved = auto()
    Attack = auto()
    TurnEnd = auto()


class MapGui:
    EV_MOVE = 'Move'
    EV_ATTACK = 'Attack'
    EV_TURN_END = 'End'

    def __init__(self, main_display, map_file):
        self.display = main_display

        # create widgets
        w, h = self.display.get_rect().size


        map_store = MapSet()
        map_store.load(map_file)

        self.cast = CharacterOrganizer()

        margin = 20
        rec1 = self.display.get_rect().inflate(-margin, -margin)

        self.map = IsoSketch(self.display.subsurface(rec1), map_store['default'], tile_size=30, tilt=60)
        # self.map.sprites = cast.all_characters()
        self.map_widget = MapWrapper(self.map)

        # self.map.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5), Pos(15, 4)], color=pygame.Color(0, 255, 0, 50)))
        # self.map.zones.append(Zone(positions=[Pos(14, 3), Pos(14, 4), Pos(14, 5), Pos(14, 6)], color=pygame.Color(0, 0, 255, 50)))

        #
        # disp.event_pos = lambda pos, etype, button: print('Event at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''


        self.char_display = CharacterDisplay(pygame.Rect(margin, h - 100 - margin, 100, 100), self.cast)
        # self.acs = ucs.ActionSelect(pygame.Rect(margin + 200, h - bottom_bar + margin, w - 2 * margin, bottom_bar - margin),
        #                       ['Move', 'Beam', 'Close'])

        self.target_display = TargetDisplay(pygame.Rect(w - 200 - margin, h - 100 - margin, 200, 100))

        self.cmd_target = None
        self.target_path = Zone([], border=pygame.Color('orange'))
        self.map.zones.append(self.target_path)

    def _draw_(self):
        self.display.fill((0, 0, 0)) # TODO should be part of Window

        # draw
        self.map_widget.draw(self.display)  #should be part pf Gui
        self.char_display.draw(self.display)
        self.target_display.draw(self.display)
        # self.acs.draw(self.display)

        pygame.display.flip()  # TODO should be part of Window

    def load_sprites_in_map(self, pcs, npcs, objects):
        for pc in pcs:
            self.cast.add_pc(pc)

        for npc in npcs:
            self.cast.add_npc(npc)

        for obj in objects:
            self.cast.add_object(obj)

        self.map.sprites = self.cast.all_characters()
        self.char_display.characters.current_pc.banner = ('main',)

    def get_action(self):
        clock = pygame.time.Clock()

        # do main loop
        while True:
            self._draw_()
            time_elapsed = clock.tick(15)

            for char in self.char_display.characters.pcs:
                char.update(time_elapsed)

            for event in pygame.event.get():
                # handle
                keys = KeyBinder({pygame.K_PAGEUP: Event('prev_char'),
                                  pygame.K_PAGEDOWN: Event('next_char'),
                                  pygame.K_ESCAPE: Event('quit'),
                                  pygame.K_q: Event('quit'),
                                  pygame.K_r: Event('rotate'),
                                  pygame.K_a: Event('pose', mode='aim'),
                                  pygame.K_s: Event('pose', mode='block'),
                                  pygame.K_d: Event('pose', mode='walk'),
                                  pygame.K_KP_ENTER: Event(MapGui.EV_TURN_END)})
                hl_events = [w.translate_event(event) for w in [self.char_display, self.map_widget, keys]]
                hl_event = next((e for e in hl_events if e is not None), Event.Empty())

                if hl_event:
                    print(repr(hl_event))

                if hl_event.is_a(MapWrapper.CLICK_LEFT):
                        # TODO display square info
                        self.map_widget.focus(hl_event)
                        self.target_display.target_pos = hl_event.pos
                        self.target_display.target = self.cast.sprite_at_pos(hl_event.pos)
                elif hl_event.is_a(MapWrapper.CLICK_RIGHT):
                    # handle action
                    player = self.char_display.characters.current_pc
                    target = self.char_display.characters.npc_at_pos(hl_event.pos)
                    if target:
                        # Attack
                        if Pos.same_place(hl_event.pos, self.cmd_target):
                            # confirmed
                            self.target_path.positions.clear()
                            self.cmd_target = None
                            return Event(self.EV_ATTACK, shooter=player, target=target)
                        else:
                            # self.target_path.positions = Flat4.trace_shot(player.pos, target.pos)
                            self.target_path.positions = Flat4.trace_shot(player.pos, target.pos)
                            self.target_path.border = pygame.Color('red')
                            self.cmd_target = target.pos
                            player.pos.dir = Flat4.dir_to(player.pos, target.pos)
                            player.set_mode('aim')
                    else:
                        # Move
                        if hl_event.pos is None:
                            self.target_path.positions.clear()
                            self.cmd_target = None
                            return hl_event

                        target_pos = hl_event.pos.but(dir=Flat4.dir_to(player.pos, hl_event.pos))
                        path = Flat4.find_path(player.pos, target_pos, self.map.is_passable)
                        if path is None:
                            self.target_path.positions.clear()
                            self.cmd_target = None
                            print('Path not possible')
                            return hl_event
                        elif Pos.same_place(hl_event.pos, self.cmd_target):
                            self.target_path.positions.clear()
                            self.cmd_target = None

                            return Event(self.EV_MOVE, player=player, pos=hl_event.pos,
                                         path=path)
                        else:
                            self.target_path.positions = path
                            self.target_path.border = pygame.Color('orange') # (255, 150, 0)
                            self.cmd_target = hl_event.pos
                            player.pos.dir = Flat4.dir_to(player.pos, hl_event.pos)
                            player.set_mode('stand')
                elif hl_event.is_a('prev_char'):
                    self.char_display.characters.current_pc.banner = None
                    self.char_display.characters.prev()
                    self.map_widget.focus(self.char_display.characters.current_pc)
                    self.char_display.characters.current_pc.banner = ('main',)
                elif hl_event.is_a('next_char'):
                    self.char_display.characters.current_pc.banner = None
                    self.char_display.characters.next()
                    self.map_widget.focus(self.char_display.characters.current_pc)
                    self.char_display.characters.current_pc.banner = ('main',)
                elif hl_event.is_a('rotate'):
                    self.char_display.characters.current_pc.pos.dir += 1
                    self.char_display.characters.current_pc.set_mode('stand')
                elif hl_event.is_a('pose'):
                    self.char_display.characters.current_pc.set_mode(hl_event.mode)
                elif hl_event.is_a('quit'):
                    return hl_event
                elif hl_event.is_a(MapGui.EV_TURN_END):
                    return hl_event

    def focus(self, object):
        # focus the view on object
        # widgets.map.set_focus(object.pos)
        self.map_widget.focus(object)

    def play_animation(self, animation: Script):
        clock = pygame.time.Clock()

        # do main loop
        while not animation.done():
            self._draw_()
            time_elapsed = clock.tick(15)

            animation.update(time_elapsed)

            for char in self.char_display.characters.pcs:
                char.update(time_elapsed)

            for char in self.char_display.characters.npcs:
                char.update(time_elapsed)



