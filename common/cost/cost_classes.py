from typing import Dict, Optional

from pydantic import BaseModel

from common.enums import Difficulty, TierLevel, UpgradeTier


class Cost(BaseModel):
    easy: int
    medium: int
    hard: int
    impopable: int

    class Config:
        use_enum_values = True

    def get_mapping(self) -> Dict[Difficulty, int]:
        return {Difficulty.easy: self.easy, Difficulty.medium: self.medium,
                Difficulty.hard: self.hard, Difficulty.impopable: self.impopable}


class Upgrade(BaseModel):
    name: str
    cost: Cost


class UpgradeTierCost(BaseModel):
    first: Upgrade
    second: Upgrade
    third: Upgrade
    fourth: Upgrade
    fifth: Upgrade
    paragon: Optional[Upgrade]

    class Config:
        use_enum_values = True

    def get_mapping(self) -> Dict[TierLevel, Upgrade]:
        return {TierLevel.first: self.first, TierLevel.second: self.second,
                TierLevel.third: self.third, TierLevel.fourth: self.fourth,
                TierLevel.fifth: self.fifth, TierLevel.paragon: self.paragon}


class UpgradesCost(BaseModel):
    top: UpgradeTierCost
    middle: UpgradeTierCost
    bottom: UpgradeTierCost

    class Config:
        use_enum_values = True

    def get_mapping(self) -> Dict[UpgradeTier, UpgradeTierCost]:
        return {UpgradeTier.top: self.top, UpgradeTier.middle: self.middle,
                UpgradeTier.bottom: self.bottom}


class TowerCost(BaseModel):
    name: str
    base_cost: Cost
    upgrades: UpgradesCost


class HeroCost(BaseModel):
    name: str
    base_cost: Cost
