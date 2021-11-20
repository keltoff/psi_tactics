from battle_logic import Pawn
from npc_ai import AI
from tile_map.data_types.position import Position
from tile_map.graphics.sprite import Sprite, IsoSprite
from enum import Enum
import pygame

Role = Enum('Role', 'PC NPC Object')


class Character(Sprite):
    def __init__(self):
        # super().__init__(None, None)

        # map facet
        self.role = None
        self.sprite = None
        self.pawn = None
        self.ai = None
        self.banner = None

        # char screen facet
        self.slot_count = 5
        self.slot_big = 1
        self.skills = []
        self.items = []
        # self.portrait = 'face'

    @classmethod
    def build(cls, sprite: Sprite = None, ai_class=None, role: Role = None, slots=5, **kwargs):
        char = Character()
        char.role = role
        char.pawn = Pawn(**kwargs)
        char.sprite = sprite

        if ai_class:
            char.ai = ai_class(char)

        # char
        char.slot_count = slots

        return char

    @property
    def pos(self):
        return self.sprite.pos

    @pos.setter
    def pos(self, pos):
        self.sprite.pos = pos

    def draw(self, target, pt):
        self.sprite.draw(target, pt)

        if self.banner:
            banner_pt = pt - (0, self.sprite.current_loop.frames[0].img.get_height())  # HACK

            cmd, *param = self.banner
            if cmd == 'countdown':
                pygame.draw.circle(target, color=pygame.Color('red'), center=banner_pt, radius=10)
                _text_(str(param[0]), pygame.Color('white'), target, banner_pt)
            if cmd == 'main':
                pygame.draw.circle(target, color=pygame.Color('blue'), center=banner_pt, radius=5)

    def update(self, time):
        self.sprite.update(time)

    def set_mode(self, mode):
        if isinstance(self.sprite, IsoSprite):
            self.sprite.set_mode(mode)


_font = pygame.font.SysFont('Comic Sans MS', 16)
def _text_(text, color, surface, pos):
    buffer = _font.render(text, False, color)
    surface.blit(buffer, (pos[0] - buffer.get_width() // 2, pos[1] - buffer.get_height() // 2))
