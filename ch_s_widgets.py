from widgets import Event, Widget
import pygame
from pygame import Rect


class CharacterWidget(Widget):
    def __init__(self, area):
        super().__init__(area)

        self.character = None

    def set_character(self, character):
        self.character = character
        self.char_update()

    def char_update(self):
        pass

    def draw(self, surface):
        'Provisional'
        pygame.draw.rect(surface, pygame.Color('Gray'), self.area, width=1)


class CharacterStats(CharacterWidget):
    def __init__(self, area):
        super().__init__(area)
        self.mods = dict()

    def draw(self, surface):
        super().draw(surface)
        # draw portrait
        # print stats
        # TODO tooltips?

        items = {'Name': self.character.name,
                 'HP': self.character.hp,
                 'Focus': self.character.focus,
                 'Psi': self.character.psi,
                 }

        first_col = self.area.copy()
        first_col.width = 80
        second_col = first_col.move(120, 0)

        # for text_block, key in _space_in_area_(self.area, items, margin=10):
        #     _text_in_area_(f'{key}:'.rjust(15, ' '), pygame.Color('Gray'), surface, text_block.clip(first_col), right=True)
        #     _text_in_area_(f'{items[key]}', pygame.Color('Gray'), surface, text_block.clip(second_col), right=True)

        for text_block, key in _space_in_area_(first_col, items, margin=10):
            _text_in_area_(f'{key}: {items[key]}', pygame.Color('Gray'), surface, text_block)

        for text_block, key in _space_in_area_(second_col, self.mods, margin=10):
            _text_in_area_(f'{key}: {self.mods[key]}', pygame.Color('Gray'), surface, text_block)

    def load_mods(self, mod_dict):
        self.mods = mod_dict


class SpritePad(CharacterWidget):
    pass


class ItemList(CharacterWidget):
    ITEM_SELECTED = 'itemlist_item_selected'
    def __init__(self, area):
        super().__init__(area)
        self.item_slots = []
        self.current_item = None

        self.visible = True

    def draw(self, surface):
        if self.visible:
            super(ItemList, self).draw(surface)

            for s in self.item_slots:
                s.draw(surface)

    def translate_event(self, event):
        hl_events = [slot.translate_event(event) for slot in self.item_slots]
        slot_event = next((e for e in hl_events if e is not None), None)
        if slot_event and self.visible:
            return Event(self.ITEM_SELECTED, item=slot_event.slot.item)
        else:
            return None


    def load_items(self, items, filter=None):
        self.item_slots = [SlotWidget(ar, parent=self, item=item) for ar, item in _space_in_area_(self.area, items, margin=10)]

    def select_item(self, slot):
        if self.current_item:
            self.current_item.deselect()

        self.current_item = slot



class ItemSlots(CharacterWidget):
    SLOT_OPENED = 'itemslots_slot_opened'
    SLOT_CLOSED = 'itemslots_slot_closed'
    SLOT_CLEAR = 'itemslots_slot_clear'

    def __init__(self, area):
        super().__init__(area=area)

        self.slots = []
        self.open_slot = None

    def draw(self, surface):
        super().draw(surface)

        for s in self.slots:
            s.draw(surface)

        # draw frame and garnish

    def translate_event(self, event):
        hl_events = [slot.translate_event(event) for slot in self.slots]
        slot_event = next((e for e in hl_events if e is not None), None)
        if slot_event is None:
            return None

        if slot_event.is_a(SlotWidget.CLICK_LEFT):
            if self.open_slot is slot_event.slot:
                self.set_open_slot(None)
                return Event(self.SLOT_CLOSED, slot=slot_event.slot)
            else:
                self.set_open_slot(slot_event.slot)
                return Event(self.SLOT_OPENED, slot=slot_event.slot)

        if slot_event.is_a(SlotWidget.CLICK_RIGHT):
            slot_event.slot.item = None
            return Event(self.SLOT_CLEAR, slot=slot_event.slot)

    def set_open_slot(self, slot):
        self.open_slot = slot

        # update_highlights
        for s in self.slots:
            s.highlight = (s is self.open_slot)

    def char_update(self):
        slot_n = self.character.slot_count
        big_n = self.character.slot_big

        if 2 * big_n > slot_n:
            big_n = slot_n // 2

        # recreate slots
        self.slots = [SlotWidget(area, parent=self) for area, n in _space_in_area_(self.area, range(slot_n), margin=10)]

class SlotWidget(Widget):
    CLICK_LEFT = 'slot_click_l'
    CLICK_RIGHT = 'slot_click_r'

    def __init__(self, area, item=None, parent=None):
        super().__init__(area)
        self.item = item
        self.color = '#0099FF'
        self.parent = parent
        self.highlight = False

    def draw(self, surface):
        if self.highlight:
            color = pygame.Color('Yellow')
        else:
            color = pygame.Color('White')

        pygame.draw.rect(surface, self.color, self.area, width=1)
        if self.item:
            _text_in_area_(str(self.item), color, surface, self.area)
        else:
            _text_in_area_('- - - - -', color, surface, self.area)

    def translate_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.area.collidepoint(event.pos):
            if event.button == 1:  # left
                return Event(self.CLICK_LEFT, slot=self)
            elif event.button == 3: # right
                return Event(self.CLICK_RIGHT, slot=self)
            else:
                return None
        else:
            return None

class SkillPanel(CharacterWidget):
    def __init__(self, area):
        super().__init__(area)

    def char_update(self):
        self.skills = self.character.skills

    def draw(self, surface):
        super().draw(surface)


class ActionPanel(CharacterWidget):
    ACTION_FOCUSED = 'action_panel_action_focused'

    def __init__(self, area):
        super().__init__(area)
        self.actions = []
        self.action_panes = []

    def char_update(self):
        # TODO update actions by items
        pass

    def draw(self, surface):
        # super().draw(surface)

        for pane_area, action in  _space_in_area_(self.area, self.actions,
                                                  lambda action: 30 + 20 * len(action.stats),
                                                  margin=5):
            if action.allow:
                txt_color = pygame.Color('White')
            else:
                txt_color = pygame.Color('#333333')

            pygame.draw.rect(surface, txt_color, pane_area, width=1)

            for line, text in _space_in_area_(pane_area,
                                              [action.name] + [f'    {key}:  {val}' for key, val in action.stats.items()],
                                              item_height=lambda i: 25 if i == action.name else 20):
                _text_in_area_(text, txt_color, surface, line.inflate(-10, 0))

    def translate_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            focused_pane = next((a for a in self.action_panes if a.collide_point(event.pos)), None)
            if focused_pane:
                return Event(self.ACTION_FOCUSED, action=focused_pane)
        return None

    def load_actions(self, actions):
        self.actions = actions


def _space_in_area_(area, items, item_height=None, margin=0):
    x0, y0 = area.topleft
    w, h = area.size

    dy = 0

    if item_height is None:
        item_height = lambda i: 30

    for i in items:
        item_h = item_height(i)
        area = Rect(x0, y0 + dy, w, item_h)
        yield area, i
        dy += item_h + margin


_font = pygame.font.SysFont('Comic Sans MS', 16)
def _text_(text, color, surface, pos):
    surface.blit(_font.render(text, False, color), pos)

def _text_in_area_(text, color, surface, area, right=False):
    text_buf = _font.render(text, False, color)

    margin = (area.height - text_buf.get_height()) // 2

    if right:
        target = text_buf.get_rect()
        target.right = area.right - margin
        target.top = area.top + margin
        surface.blit(text_buf, target)
    else:
        surface.blit(text_buf, (area.left + margin, area.top + margin))