from dataclasses import dataclass


@dataclass
class Tower:
    x: int
    y: int
    top: int = 0
    middle: int = 0
    bottom: int = 0
    targeting: int = 0
    special_targeting: int = 0
