from typing import Dict, Optional

from pydantic import BaseModel

from common.game_classes.enums import Difficulty, TierLevel, UpgradeTier, TowerType


class Cost(BaseModel):
    easy: int
    medium: int
    hard: int
    impopable: int

    class Config:
        use_enum_values = True

    def get_mapping(self) -> dict[Difficulty, int]:
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

    def get_mapping(self) -> dict[TierLevel, Upgrade]:
        return {TierLevel.first: self.first, TierLevel.second: self.second,
                TierLevel.third: self.third, TierLevel.fourth: self.fourth,
                TierLevel.fifth: self.fifth, TierLevel.paragon: self.paragon}


class UpgradesCost(BaseModel):
    top: UpgradeTierCost
    middle: UpgradeTierCost
    bottom: UpgradeTierCost

    class Config:
        use_enum_values = True

    def get_mapping(self) -> dict[UpgradeTier, UpgradeTierCost]:
        return {UpgradeTier.top: self.top, UpgradeTier.middle: self.middle,
                UpgradeTier.bottom: self.bottom}


class TowerInfo(BaseModel):
    name: str
    type: TowerType
    base_cost: Cost
    upgrades: UpgradesCost

    class Config:
        use_enum_values = True


class HeroInfo(BaseModel):
    name: str
    base_cost: Cost
