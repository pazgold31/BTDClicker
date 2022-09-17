from dataclasses import dataclass, field
from typing import Dict

from common.game_classes.enums import UpgradeTier


@dataclass
class BaseTower:
    name: str
    x: int
    y: int


@dataclass
class Tower(BaseTower):
    tier_map: Dict[UpgradeTier, int] = field(default_factory=lambda: {i: 0 for i in UpgradeTier})
    targeting: int = 0
    special_targeting: int = 0


@dataclass
class Hero(BaseTower):
    targeting: int = 0
    special_targeting: int = 0
