import random
from typing import Literal


Difficulty = Literal['easy', 'medium', 'hard', 'deadly']

DifficultySets = ['peaceful', 'tamed', 'untamed', 'dangerous', 'inhospitable', 'alien']

DifficultySet = Literal[*DifficultySets]

_numeric_crs = [str(x) for x in range(40)]
CR = Literal[*(['0', '1/8', '1/4', '1/2'] + _numeric_crs)]


def to_numeric_cr(cr: str):
    cr = str(cr)
    try:
        return float(cr)
    except ValueError:
        num, denom = cr.split('/')
        return float(num) / float(denom)


def roll_dice(dice_to_roll: str) -> int:
    """
    Return the result of rolling some dice.

    Examples: 5d10+4, 2d4, 7, 3d5+2d3

    :param dice_to_roll: A string representing the dice that are rolled.
    """
    dice_to_roll = dice_to_roll.replace(' ', '')
    dice_to_roll = dice_to_roll.replace('-', '+-')
    pieces = dice_to_roll.split('+')
    result = 0
    for piece in pieces:
        if 'd' in piece:
            number, size = piece.split('d')
            result += sum([random.randint(1, int(size)) for _ in range(int(number))])
        else:
            result += int(piece)
    return result
