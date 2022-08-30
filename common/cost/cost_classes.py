from dataclasses import dataclass
from typing import Dict, Optional

from common.enums import Difficulty, TierLevel, UpgradeTier


@dataclass
class Cost:
    easy: int
    medium: int
    hard: int
    chimps: int

    def get_mapping(self) -> Dict[Difficulty, int]:
        return {Difficulty.easy: self.easy, Difficulty.medium: self.medium,
                Difficulty.hard: self.hard, Difficulty.chimps: self.chimps}


@dataclass
class Upgrade:
    name: str
    cost: Cost


@dataclass
class UpgradeTierCost:
    first: Cost
    second: Cost
    third: Cost
    fourth: Cost
    fifth: Cost
    paragon: Optional[Cost]

    def get_mapping(self) -> Dict[TierLevel, Cost]:
        return {TierLevel.first: self.first, TierLevel.second: self.second,
                TierLevel.third: self.third, TierLevel.fourth: self.fourth,
                TierLevel.fifth: self.fifth, TierLevel.paragon: self.paragon}


@dataclass
class UpgradesCost:
    top: UpgradeTierCost
    middle: UpgradeTierCost
    bottom: UpgradeTierCost

    def get_mapping(self) -> Dict[UpgradeTier, UpgradeTierCost]:
        return {UpgradeTier.top: self.top, UpgradeTier.middle: self.middle,
                UpgradeTier.bottom: self.bottom}


@dataclass
class TowerCost:
    name: str
    base_cost: Cost
    upgrades: UpgradesCost
