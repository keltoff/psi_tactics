from enum import Enum, auto
from collections import namedtuple
import battle_logic as bl
from map_gui import MapGui, Event
from animations import ScriptWalk, ScriptAttack, ScriptSpin
from tile_map.data_types.position import Position as Pos
from enum import Enum, auto
from math import inf
import pygame
from pygame import Rect
from collections import namedtuple
from widgets import Event, CharacterOrganizer, CharacterDisplay, KeyBinder, MapWrapper, TargetDisplay
from ch_s_widgets import CharacterStats, ItemList, ItemSlots, SkillPanel, SpritePad, CharacterWidget, SlotWidget
from tile_map.map_display import Display
from tile_map.map_display import IsoSketch
from tile_map.map_storage.map_storage import MapSet
from tile_map.graphics.storage import Storage
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.topology import *
from tile_map.gui import Gui
from animations import Script



class CharacterScreen:
    def __init__(self, game_window):
        self.gui = CharacterGui(game_window)
        self.characters = CharacterOrganizer()
        self.item_data = []

    def view_characters(self, characters, item_data):

        for char in characters:
            self.characters.add_pc(char)

        self.item_data = item_data

        self.gui.item_list.load_items(self.item_data, None)
        self.gui.update_character(self.characters.current_pc)

        while True:
            action = self.gui.get_action()

            # handle
            if action.is_a('prev_char'):
                self.characters.prev()
                self.gui.update_character(self.characters.current_pc)
            elif action.is_a('next_char'):
                self.characters.next()
                self.gui.update_character(self.characters.current_pc)
            elif action.is_a('quit'):
                break

        # finalize changes
        # possibly persist characters

class CharacterGui:
    def __init__(self, display):
        self.display = display

        self.char_stats = CharacterStats(area=Rect(50, 100, 200, 200))
        self.item_list = ItemList(area=Rect(50, 350, 200, 300))
        self.sprite_pad = SpritePad(area=Rect(300, 100, 200, 200))
        self.slots = ItemSlots(area=Rect(300, 350, 200, 300))
        self.skill_panel = SkillPanel(area=Rect(550, 100, 200, 550))

        self.widgets = [self.char_stats, self.item_list, self.sprite_pad, self.slots, self.skill_panel]

    def _draw_(self):
        self.display.fill((0, 0, 0)) # TODO should be part of Window

        # draw
        for w in self.widgets:
            w.draw(self.display)

        pygame.display.flip()  # TODO should be part of Window

    def update_character(self, character):
        for w in self.widgets:
            if isinstance(w, CharacterWidget):
                w.set_character(character)

    def get_action(self):
        clock = pygame.time.Clock()

        # do main loop
        while True:
            self._draw_()
            time_elapsed = clock.tick(15)

            # for char in self.char_display.characters.pcs:
            #     char.update(time_elapsed)

            for event in pygame.event.get():
                # handle
                keys = KeyBinder({pygame.K_PAGEUP: Event('prev_char'),
                                  pygame.K_PAGEDOWN: Event('next_char'),
                                  pygame.K_ESCAPE: Event('quit'),
                                  pygame.K_q: Event('quit'),
                                  })
                hl_events = [w.translate_event(event) for w in self.widgets + [keys]]
                hl_event =  next((e for e in hl_events if e is not None), Event.Empty())

                if hl_event:
                    print(repr(hl_event))

                if hl_event.is_a(ItemSlots.SLOT_OPENED):
                    pass
                if hl_event.is_a(ItemSlots.SLOT_CLOSED):
                    pass
                if hl_event.is_a(ItemList.ITEM_SELECTED) and self.slots.open_slot:
                    self.slots.open_slot.item = hl_event.item
                    self.slots.set_open_slot(None)
                    Event('Equip update', char=self.slots.character)

                # if hl_event.is_a(SlotWidget.CLICK_LEFT):
                #     if hl_event.slot.parent is self.item_list:
                #         self.item_list.select_item(hl_event.slot)
                #     if hl_event.slot.parent is self.slots:
                #         if self.item_list.current_item:
                #             hl_event.slot.item = self.item_list.current_item
                #             self.item_list.select_item(None)
                #             return Event('Equip update', char=self.slots.character)
                #
                # elif hl_event.is_a(SlotWidget.CLICK_RIGHT):
                #     if hl_event.slot.parent is self.slots:
                #         hl_event.slot.item = None

                elif hl_event.is_in(['prev_char', 'next_char', 'quit']):
                    return hl_event

    def transfer_item(self, item, slot):
        pass

class Character:
    def __init__(self, name, hp, focus, psi, portrait_key, slots=5):
        self.name = name
        self.hp = hp
        self.focus = focus
        self.psi = psi
        self.portrait = portrait_key

        self.slot_count = slots
        self.slot_big = 1

        self.skills = []


if __name__ == '__main__':
    # create the screen gui

    characters = [Character(name=f'Char {i}', hp=3 + i, focus=10 - i, psi=i, portrait_key='face', slots= 4+i) for i in range(3)]

    items = ['Stunner', 'Grenade', 'Toolkit', 'Shield', 'Smokebomb']


    # TODO move to main_loop
    import pygame
    pygame.init()
    window = pygame.display.set_mode((800, 700))

    # screen = MapScreen(window, map_file='data/mapdata.xml')
    screen = CharacterScreen(window)
    screen.view_characters(characters, item_data=items)
