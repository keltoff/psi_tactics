from enum import Enum, auto
import pygame
from collections import namedtuple
from widgets import Event, CharacterOrganizer, CharacterDisplay, KeyBinder, MapWrapper
from tile_map.map_display import Display
from tile_map.map_display import IsoSketch
from tile_map.map_storage.map_storage import MapSet
from tile_map.graphics.storage import Storage
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.topology import *
from tile_map.gui import Gui


class MapGuiEvents(Enum):
    PlayerMoved = auto()
    Attack = auto()
    TurnEnd = auto()


class MapGui:
    EV_MOVE = 'Move'
    EV_ATTACK = 'Attack'
    EV_TURN_END = 'End'

    def __init__(self, main_display):
        self.display = main_display

        # create widgets
        w, h = self.display.get_rect().size


        map_store = MapSet()
        map_store.load('data/mapdata.xml')

        # sprite_storage = Storage.load('data/graphics_iso.xml')
        sprite_storage = Storage.load('data/sprites.xml')

        cast = CharacterOrganizer()
        cast.add_pc(sprite_storage.make_sprite('war', Pos(13, 5, d=0)))
        cast.add_pc(sprite_storage.make_sprite('jen', Pos(11, 4, d=1)))

        margin = 20
        rec1 = self.display.get_rect().inflate(-margin, -margin)

        self.map = IsoSketch(self.display.subsurface(rec1), map_store['default'], tile_size=30, tilt=60)
        self.map.sprites = cast.pcs
        self.map_widget = MapWrapper(self.map)

        # disp.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5)], color=pygame.Color(0, 255, 0, 50)))
        #
        # disp.event_pos = lambda pos, etype, button: print('Event at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''


        self.char_display = CharacterDisplay(pygame.Rect(margin, h - 100 - margin, 100, 100), cast)
        # self.acs = ucs.ActionSelect(pygame.Rect(margin + 200, h - bottom_bar + margin, w - 2 * margin, bottom_bar - margin),
        #                       ['Move', 'Beam', 'Close'])

    def _draw_(self):
        self.display.fill((0, 0, 0)) # TODO should be part of Window

        # draw
        self.map_widget.draw(self.display)  #should be part pf Gui
        self.char_display.draw(self.display)
        # self.acs.draw(self.display)

        pygame.display.flip()  # TODO should be part of Window

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
                                  pygame.K_d: Event('pose', mode='walk')})
                hl_events = [w.translate_event(event) for w in [self.char_display, self.map_widget, keys]]
                hl_event =  next((e for e in hl_events if e is not None), Event.Empty())

                if hl_event:
                    print(repr(hl_event))

                if hl_event.is_a(MapWrapper.CLICK_LEFT):
                        # TODO display square info
                        self.map_widget.focus(hl_event)
                elif hl_event.is_a(MapWrapper.CLICK_RIGHT):
                    # handle action
                    player = self.char_display.characters.current_pc
                    target = self.char_display.characters.nps_at_pos(hl_event.pos)
                    if target:
                        return Event(self.EV_ATTACK, shooter=player, target=target)
                    else:
                        return Event(self.EV_MOVE, player=player, pos=hl_event.pos)
                elif hl_event.is_a('prev_char'):
                    self.char_display.characters.prev()
                    self.map_widget.focus(self.char_display.characters.current_pc)
                elif hl_event.is_a('next_char'):
                    self.char_display.characters.next()
                    self.map_widget.focus(self.char_display.characters.current_pc)
                elif hl_event.is_a('rotate'):
                    self.char_display.characters.current_pc.pos.dir += 1
                    self.char_display.characters.current_pc.set_mode('stand')
                elif hl_event.is_a('pose'):
                    self.char_display.characters.current_pc.set_mode(hl_event.mode)
                elif hl_event.is_a('quit'):
                    return hl_event

    def focus(self, object):
        # focus the view on object
        # widgets.map.set_focus(object.pos)
        self.map_widget.focus(object)

    def play_animation(self, animation_type, *actors):
        pass