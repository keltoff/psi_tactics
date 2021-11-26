from enum import Enum, auto
from math import inf
import pygame
from collections import namedtuple

import animations
from widgets import Event, CharacterOrganizer, CharacterDisplay, KeyBinder, MapWrapper, TargetDisplay, Widget
from tile_map.map_display import Display
from tile_map.map_display import IsoSketch
from tile_map.map_storage.map_storage import MapSet
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.topology import *
import animations as ani
from tile_map.gui import Gui


from enum import Enum, auto
from collections import namedtuple
import battle_logic as bl
from map_gui import MapGui, Event
from animations import ScriptWalk, ScriptAttack, ScriptSpin
from tile_map.data_types.position import Position as Pos
from dataclasses import dataclass
import npc_ai
# from character import Character, Role
from tile_map.graphics.storage import Storage
from tile_map.graphics.sprite import Sprite
from functools import singledispatchmethod
from ch_s_widgets import _text_in_area_, _text_


class DialogWidget(Widget):
    DONE = 'dialog_done'

    def __init__(self):
        super().__init__(pygame.Rect(100, 600, 600, 50))

        self.character = None
        self.text = None

    def set(self, text=None, character=None):
        self.text = text
        self.character = character

    def draw(self, surface):
        if self.text:
            pygame.draw.rect(surface, pygame.color.Color('darkgray'), self.area, width=0)
            pygame.draw.rect(surface, pygame.color.Color('cyan'), self.area.inflate(-10, -10), width=2)

            _text_in_area_(self.text, pygame.Color('black'), surface, self.area.inflate(-20, -20))

            if self.character:
                _text_(str(self.character), pygame.Color('cyan'), surface, (self.area.left + 20, self.area.top -30))

    def translate_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.area.collidepoint(event.pos) and event.button == 1:  # left
                return Event(self.DONE)
        else:
            keys = KeyBinder({pygame.K_KP_ENTER: Event(self.DONE),
                              pygame.K_RETURN: Event(self.DONE),
                              pygame.K_SPACE: Event(self.DONE),
                              })

            return keys.translate_event(event)


class EventScreen:
    def __init__(self, window):
        self.display = window
        self.cast = CharacterOrganizer()

        self.map = None
        self.map_widget = None

        self.dialog = DialogWidget()

    @singledispatchmethod
    def say(self, character, text):
        # print(f'[{character}]: \"{text}\"')
        self.dialog.set(text, character=character)

        self.get_action()

        self.dialog.set()

    @say.register
    def _(self, text: str):
        # print(text)
        self.say(None, text)

    def set_scene(self, map_file, characters, focus):
        map_store = MapSet()
        map_store.load(map_file)

        # map
        self.map = IsoSketch(self.display, map_store['default'], tile_size=30, tilt=60)
        self.map_widget = MapWrapper(self.map)

        # characters
        self.map.sprites = characters

        # focus
        self.focus(focus)

    def play_event(self, event):
        event(self.set_scene, self.say, self.play_animation)

    def _draw_(self):
        self.display.fill((0, 0, 0))  # TODO should be part of Window

        # draw
        self.map_widget.draw(self.display)  #should be part pf Gui
        self.dialog.draw(self.display)

        pygame.display.flip()  # TODO should be part of Window


    def get_action(self):
        clock = pygame.time.Clock()

        # do main loop
        while True:
            self._draw_()
            time_elapsed = clock.tick(15)

            for char in self.cast.pcs: # all characters
                char.update(time_elapsed)

            for event in pygame.event.get():
                hl_event = self.dialog.translate_event(event)
                if hl_event is not None and hl_event.is_a(DialogWidget.DONE):
                    return DialogWidget.DONE

    def focus(self, object):
        # focus the view on object
        self.map_widget.focus(object)

    def play_animation(self, animation: ani.Script):
        clock = pygame.time.Clock()

        # do main loop
        while not animation.done():
            self._draw_()
            time_elapsed = clock.tick(15)

            animation.update(time_elapsed)

            for s in self.map.sprites:
                s.update(time_elapsed)

            # for char in self.cast.pcs:
            #     char.update(time_elapsed)
            #
            # for char in self.cast.npcs:
            #     char.update(time_elapsed)


@dataclass()
class Character:
    name: str
    portrait: Sprite
    sprite: Sprite

    def __init__(self, name, portrait, sprite):
        self.name = name
        self.sprite = sprite

    def __str__(self):
        return self.name

    @property
    def pos(self):
        return self.sprite.pos

    @pos.setter
    def pos(self, value):
        self.sprite.pos = value

    def draw(self, surface, s_pt):
        self.sprite.draw(surface, s_pt)

    def update(self, elapsed_time):
        self.sprite.update(elapsed_time)

    def set_mode(self, mode):
        self.sprite.set_mode(mode)


def chat_event(set_scene, say, play):
    # def set_scene(**kwargs): pass
    # def say(*args): pass
    # def play(animation: ani.Script): pass

    store = Storage.load('data/sprites.xml')
    face_store = {'face_alice': None,
                  'face_bob': None}

    alice = Character(name='Alice', portrait=face_store['face_alice'], sprite=store.make_sprite('jen', Pos(5, 5, d=1)))
    bob = Character(name='Bob', portrait=face_store['face_bob'], sprite=store.make_sprite('war', Pos(20, 5, d=3)))

    set_scene(map_file='data/mapdata_flat.xml', characters=[alice, bob], focus=Pos(13, 5))
    topology = Flat4

    say(f'{alice} and {bob} met in the dark alley.')

    play(ani.Simultaneously(ani.ScriptWalk(alice, topology.find_path(alice.pos, Pos(10, 5, d=1))),
                            ani.ScriptWalk(bob, topology.find_path(bob.pos, Pos(15, 5, d=3)))
                            ))

    say(alice, f'Hi {bob}')
    say(bob, f'Hi {alice}. What\'s up?')
    say(alice, 'Robbery, that\'s what.')
    play(ani.ScriptAim(alice, bob))
    say(alice, f'Hands up, {bob}.')
    # play(ani.ScriptSpin(bob))

    say(bob, 'What? What? What?')
    say(alice, 'Your money or your life. Pay up or you\'re toast.')

    bob.pos = bob.pos.but(dir=2)  # bob.pos.dir = 2

    say(bob, 'Okay, I have my wallet right here ...')
    # bob.pos.dir = topology.dir_to(bob.pos, alice.pos)
    bob.pos = bob.pos.but(dir=topology.dir_to(bob.pos, alice.pos))
    say(bob, '... next to my gun !')
    play(ani.Simultaneously(ani.ScriptAim(bob, alice),
                            ani.ScriptAttack(alice, bob, None)
                            ))
    bob.set_mode('is_hit')
    # bob.visible = False

    say(bob, 'Ouch!')

    say(alice, '...')
    play(ani.ScriptWalk(alice, topology.find_path(alice.pos, bob.pos.fwd().but(dir=alice.pos.dir))))
    say(alice, f'20 bucks and a candy bar? Really, {bob}? That\'s what you were willing to die for?')
    say(bob, 'Hey, this brand is my favorite !')

    say('* badum tish *')


if __name__ == '__main__':
    # create the screen gui

    # TODO move to main_loop
    import pygame
    pygame.init()
    window = pygame.display.set_mode((800, 700))

    screen = EventScreen(window)
    screen.play_event(chat_event)
