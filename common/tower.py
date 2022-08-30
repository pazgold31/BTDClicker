from dataclasses import dataclass, field
from typing import Dict

from common.enums import UpgradeTier


@dataclass
class Tower:
    name: str
    x: int
    y: int
    tier_map: Dict[UpgradeTier, int] = field(default_factory=lambda: {i: 0 for i in UpgradeTier})
    targeting: int = 0
    special_targeting: int = 0
