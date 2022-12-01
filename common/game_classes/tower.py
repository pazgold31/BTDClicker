from typing import Dict

from pydantic import BaseModel

from common.game_classes.enums import UpgradeTier


class BaseTower(BaseModel):
    x: int
    y: int

    sold: bool = False
    targeting: int = 0
    s_targeting: int = 0


class Tower(BaseTower):
    name: str
    tier_map: Dict[UpgradeTier, int] = {i: 0 for i in UpgradeTier}


class Hero(BaseTower):
    pass
