from enum import IntEnum


class Difficulty(IntEnum):
    easy = 1,
    medium = 2,
    hard = 3,
    impopable = 4


class TierLevel(IntEnum):
    first = 1,
    second = 2,
    third = 3,
    fourth = 4
    fifth = 5
    paragon = 6


class UpgradeTier(IntEnum):
    top = 1,
    middle = 2,
    bottom = 3


class TowerType(IntEnum):
    Primary = 0
    Military = 1
    Magic = 2
    Support = 3
