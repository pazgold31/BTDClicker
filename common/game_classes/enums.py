from enum import IntEnum, Enum


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


class TowerType(Enum):
    Primary = "Primary Monkeys"
    Military = "Military Monkeys"
    Magic = "Magic Monkeys"
    Support = "Support Monkeys"
