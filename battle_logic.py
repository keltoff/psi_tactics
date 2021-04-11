from dataclasses import dataclass

# PLaceholder classes, before linking them properly
class Character:
    def __init__(self):
        self.moved = False
        self.acted = False
        self.visible = True

class Pos:
    pass

# Event classes
@dataclass
class Action:
    def is_a(self, action_type):
        return isinstance(self, action_type)

@dataclass
class Attack(Action):
    player : Character
    target: Character


@dataclass
class Move(Action):
    player: Character
    position: Pos


def check_move_legal(action):
    return True

def check_attack_legal(action):
    return False


def process_attack(shooter, target):
    # COmpute damage etc etc

    result = None
    return result


def apply_attack(effect, shooter, target):
    # target.HP -= effect.damage
    pass