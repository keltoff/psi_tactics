from dataclasses import dataclass
from tile_map.data_types.position import Position as Pos


class Stat:
    def __init__(self, max, val=None):
        self.max = max

        if val is None:
            self.val = max
        else:
            self.val = val

    def __add__(self, other):
        new_val = min(self.val + other, self.max)
        return Stat(val=new_val, max=self.max)

    def __sub__(self, other):
        new_val = max(self.val - other, 0)
        return Stat(val=new_val, max=self.max)

    def __str__(self):
        return f'{self.val} / {self.max}'

    def pay(self, x):
        if self.val >= x:
            self.val -= x
            return True
        else:
            return False

    def hit(self, x):
        self.val = max(0, self.val - x)
        return self.val == 0


class Pawn:
    def __init__(self, name, hp, focus, psi=None):
        self.name = name
        self.hp = Stat(hp)
        self.focus = Stat(focus)
        self.psi = psi


# Placeholder classes, before linking them properly
class Character(Pawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moved = False
        self.acted = False
        self.visible = True


# Event classes
@dataclass
class Action:
    def is_a(self, action_type):
        return isinstance(self, action_type)


@dataclass
class Attack(Action):
    player: Character
    target: Character


@dataclass
class Move(Action):
    player: Character
    position: Pos


def check_move_legal(action):
    return True


def check_attack_legal(action):
    return True


def process_attack(shooter, target):
    # Compute damage etc etc

    result = 1
    return result


def apply_attack(effect, shooter, target):
    shooter.focus.pay(1)
    if target.hp.hit(effect):
        print('They died')
