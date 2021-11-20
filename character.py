from battle_logic import Pawn
from npc_ai import AI
from tile_map.data_types.position import Position
from tile_map.graphics.sprite import Sprite, IsoSprite
from enum import Enum

Role = Enum('Role', 'PC NPC Object')


class Character(Sprite):
    def __init__(self):
        # super().__init__(None, None)

        # map facet
        self.role = None
        self.sprite = None
        self.pawn = None
        self.ai = None

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

    def update(self, time):
        self.sprite.update(time)

    def set_mode(self, mode):
        if isinstance(self.sprite, IsoSprite):
            self.sprite.set_mode(mode)
