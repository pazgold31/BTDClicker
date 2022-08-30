from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Optional


class CostIndex(IntEnum):
    easy = 1,
    medium = 2,
    hard = 3,
    chimps = 4


class UpgradeTierCostIndex(IntEnum):
    first = 1,
    second = 2,
    third = 3,
    fourth = 4
    fifth = 5
    paragon = 6


class UpgradeCostIndex(IntEnum):
    top = 1,
    middle = 2,
    bottom = 3


@dataclass
class Cost:
    easy: int
    medium: int
    hard: int
    chimps: int

    def get_mapping(self) -> Dict[CostIndex, int]:
        return {CostIndex.easy: self.easy, CostIndex.medium: self.medium,
                CostIndex.hard: self.hard, CostIndex.chimps: self.chimps}


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

    def get_mapping(self) -> Dict[int, Cost]:
        return {UpgradeTierCostIndex.first: self.first, UpgradeTierCostIndex.second: self.second,
                UpgradeTierCostIndex.third: self.third, UpgradeTierCostIndex.fourth: self.fourth,
                UpgradeTierCostIndex.fifth: self.fifth, UpgradeTierCostIndex.paragon: self.paragon}


@dataclass
class UpgradesCost:
    top: UpgradeTierCost
    middle: UpgradeTierCost
    bottom: UpgradeTierCost

    def get_mapping(self) -> Dict[int, UpgradeTierCost]:
        return {UpgradeCostIndex.top: self.top, UpgradeCostIndex.middle: self.middle,
                UpgradeCostIndex.bottom: self.bottom}


@dataclass
class TowerCost:
    name: str
    base_cost: Cost
    upgrades: UpgradesCost
