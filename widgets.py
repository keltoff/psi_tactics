# from .graphics.sprite import Sprite
from tile_map.data_types.coords_ex import Pt, Dir
import pygame
from itertools import count


class Event:
    def __init__(self, type, **kwargs):
        self.type = type
        self.properties = kwargs

    def __getattr__(self, item):
        if item in self.properties:
            return self.properties[item]
        else:
            raise AttributeError(f'Event does not have \'{item}\'.')

    def __eq__(self, other):
        if isinstance(other, str):
            return self.is_a(other)
        elif isinstance(other, Event):
            return self.type == other.type and self.properties == other.properties
        else:
            return False

    def __bool__(self):
        return self.type is not None

    def __repr__(self):
        prop_list = '|'.join(f'{p}: {str(self.properties[p])}' for p in self.properties)
        return f'{self.type} [{prop_list}]'

    def is_a(self, type):
        return self.type == type

    def is_in(self, types):
        return any(self.is_a(t) for t in types)

    @classmethod
    def Empty(cls):
        return Event(None)




class Widget:
    def __init__(self, area):
        self.area = area
        self.cursor = None

    def draw(self, surface):
        pass

    def get_cursor(self, pos):
        return self.cursor

    def translate_event(self, event):
        return None


class KeyBinder:
    def __init__(self, event_dictionary):
        self.dict = event_dictionary

    def translate_event(self, event):
        if event.type == pygame.KEYDOWN:
            return self.dict.get(event.key, None)
        else:
            return None


class MapWrapper(Widget):
    CLICK_LEFT = 'click_left'
    CLICK_RIGHT = 'click_right'

    def __init__(self, map):
        super().__init__(map.area)
        self.map = map

    def draw(self, surface):
        self.map.draw()  # already has reference to surface
        # TODO change that?

    def focus(self, target):
        pos = getattr(target, 'pos', None)
        if pos:
            self.map.center_pos = pos
            self.map.selected_tile = pos

    def translate_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            click_pos = self.map.pt_to_pos(event.pos)
            if event.button == 1:  # left
                return Event(self.CLICK_LEFT, pos=click_pos)
            elif event.button == 3:  # right
                return Event(self.CLICK_RIGHT, pos=click_pos)
            else:  # other buttons?
                return None
        else:
            return None


class CharacterOrganizer:
    def __init__(self):
        self.pcs = []
        self.npcs = []
        self.objects = []
        self.current = 0

    def add_pc(self, character):
        self.pcs.append(character)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_object(self, obj):
        self.objects.append(obj)

    @property
    def current_pc(self):
        if len(self.pcs) <= self.current:
            return None
        else:
            return self.pcs[self.current]

    def prev(self):
        self.current -= 1
        if self.current < 0:
            self.current = len(self.pcs) - 1

    def next(self):
        self.current += 1
        if self.current >= len(self.pcs):
            self.current = 0

    def npc_at_pos(self, pos):
        return next((npc for npc in self.npcs + self.objects if npc.pos.same_place(pos)), None)

    def sprite_at_pos(self, pos):
        return next((s for s in self.all_characters() if s.pos.same_place(pos)), None)

    def all_characters(self):
        return self.pcs + self.npcs + self.objects


class CharacterDisplay(Widget):
    def __init__(self, area, character_set: CharacterOrganizer):
        super().__init__(area)

        self.characters = character_set

    def draw(self, surface):
        character = self.characters.current_pc

        pygame.draw.rect(surface, pygame.Color('White'), self.area, 1)

        character.draw(surface, Pt(self.area.centerx, self.area.bottom - 20, dir=Dir(1)))


pygame.font.init()

class TargetDisplay(Widget):
    def __init__(self, area):
        super().__init__(area)

        self.target_pos = None
        self.target = None

        self.font = pygame.font.SysFont('Comic Sans MS', 16)

    def draw(self, surface):
        # if self.target_pos is None:
        #     return

        # draw ground

        # draw object
        target = self.target
        cx, cy = self.area.center

        if target:
            pawn = target.pawn

            pygame.draw.rect(surface, pygame.Color('black'), self.area, 0)
            pygame.draw.rect(surface, pygame.Color('White'), self.area, 1)

            target.draw(surface, Pt(self.area.centerx - 50, self.area.centery + 20, dir=Dir(1)))

            y_steps = (cy - 45 + i * 20 for i in count())

            textsurface = self.font.render(pawn.name, False, pygame.Color('gray'))
            surface.blit(textsurface, (cx, next(y_steps)) )

            textsurface = self.font.render(str(pawn.hp), False, pygame.Color('red'))
            surface.blit(textsurface, (cx, next(y_steps)))

            textsurface = self.font.render(str(pawn.focus), False, pygame.Color('blue'))
            surface.blit(textsurface, (cx, next(y_steps)))

            text = str(pawn.psi) if pawn.psi else f'-- / --'
            textsurface = self.font.render(text, False, pygame.Color('green'))
            surface.blit(textsurface, (cx, next(y_steps)))


class Switch(Widget):
    def __init__(self, area, label):
        super().__init__(area)
        self.color = pygame.Color('yellow')
        self.on = False
        self.cursor = 'hand'

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color('gray'), self.area, 2)

        if self.on:
            pygame.draw.rect(surface, self.color, self.area.inflate(-6, -6), 2)

    def click(self, pos, button):
        if button == 1:
            self.on = not self.on


class ActionSelect(Widget):
    def __init__(self, area, actions):
        super().__init__(area)

        self.actions = actions
        self.selected_idx = None

        button_h, button_w = 30, 60
        margin = 5

        first_btn_rect = pygame.Rect(self.area.left, self.area.top, button_w, button_h)
        self.buttons = [Switch(first_btn_rect.move(i * (button_w + margin), 0), a) for i, a in enumerate(actions)]

    def draw(self, surface):
        for b in self.buttons:
            b.draw(surface)

    def click(self, pos, button):
        if button == 1:
            for i, b in enumerate(self.buttons):
                if b.area.collidepoint(pos):
                    self.button_clicked(i)

    def button_clicked(self, idx):
        for i, b in enumerate(self.buttons):
            b.on = idx == i

        self.selected_idx = idx
        print(self.selected)

    @property
    def selected(self):
        if self.selected_idx is None:
            return None
        else:
            return self.actions[self.selected_idx]
