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
        cast.add_npc(sprite_storage.make_sprite('red', Pos(9, 3, d=2)))
        cast.add_npc(sprite_storage.make_sprite('red', Pos(12, 3, d=2)))
        cast.add_npc(sprite_storage.make_sprite('red', Pos(15, 3, d=2)))
        cast.add_npc(sprite_storage.make_sprite('red', Pos(8, 5, d=1)))
        cast.add_npc(sprite_storage.make_sprite('red', Pos(16, 5, d=3)))

        margin = 20
        rec1 = self.display.get_rect().inflate(-margin, -margin)

        self.map = IsoSketch(self.display.subsurface(rec1), map_store['default'], tile_size=30, tilt=60)
        self.map.sprites = cast.all_characters()
        self.map_widget = MapWrapper(self.map)

        # self.map.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5), Pos(15, 4)], color=pygame.Color(0, 255, 0, 50)))
        # self.map.zones.append(Zone(positions=[Pos(14, 3), Pos(14, 4), Pos(14, 5), Pos(14, 6)], color=pygame.Color(0, 0, 255, 50)))

        #
        # disp.event_pos = lambda pos, etype, button: print('Event at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''


        self.char_display = CharacterDisplay(pygame.Rect(margin, h - 100 - margin, 100, 100), cast)
        # self.acs = ucs.ActionSelect(pygame.Rect(margin + 200, h - bottom_bar + margin, w - 2 * margin, bottom_bar - margin),
        #                       ['Move', 'Beam', 'Close'])

        self.cmd_target = None
        self.target_path = Zone([], border=pygame.Color('orange'))
        self.map.zones.append(self.target_path)

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
                        # Attack
                        if Pos.same_place(hl_event.pos, self.cmd_target):
                            # confirmed
                            self.target_path.positions.clear()
                            self.cmd_target = None
                            return Event(self.EV_ATTACK, shooter=player, target=target)
                        else:
                            self.target_path.positions = Flat4.trace_shot(player.pos, target.pos)
                            self.target_path.border = pygame.Color('red')
                            self.cmd_target = target.pos
                            player.pos.dir = Flat4.dir_to(player.pos, target.pos)
                            player.set_mode('aim')
                    else:
                        # Move
                        if Pos.same_place(hl_event.pos, self.cmd_target):
                            self.target_path.positions.clear()
                            self.cmd_target = None
                            return Event(self.EV_MOVE, player=player, pos=hl_event.pos)
                        else:
                            self.target_path.positions = Flat4.find_path(player.pos, hl_event.pos)
                            self.target_path.border = pygame.Color('orange') # (255, 150, 0)
                            self.cmd_target = hl_event.pos
                            player.pos.dir = Flat4.dir_to(player.pos, hl_event.pos)
                            player.set_mode('stand')
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
        # clock = pygame.time.Clock()
        #
        # # do main loop
        # while True:
        #     self._draw_()
        #     time_elapsed = clock.tick(15)
        #
        #     for char in self.char_display.characters.pcs:
        #         char.update(time_elapsed)


class Script:
    def __init__(self, type, **params):
        self.type = type
        self.params = params
        self.t = 0

    def update(self, time):
        self.t += time

    def done(self):
        return True

    def wait(self, time):
        pass


class ScriptSin(Script):
    def __init__(self, actor):
        super().__init__('Puppet')
        self.actor = actor

    def update(self, time):
        super().update(time)

    def play_out(self):
        self.actor.set_mode('spin')

        self.wait(1000)

        self.actor.set_mode('stand')


class ScriptAttack(Script):
    def __init__(self, actor, target):
        super().__init__('Puppet')
        self.actor = actor
        self.target = target

    def update(self, time):
        super().update(time)

    def play_out(self):
        self.actor.pos.dir = geometry.dir_towards(self.actor.pos, self.target.pos)
        self.actor.set_mode('aim')

        self.wait(500)

        add_effect('Beam', self.actor, self.target)
        self.target.set_mode('is_hit')

        self.wait(500)

        self.actor.set_mode('stand')
        self.target.set_mode('stand')
        # remove_effect ??

