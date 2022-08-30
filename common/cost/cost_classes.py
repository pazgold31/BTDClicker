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
    One: Cost
    Two: Cost
    Three: Cost
    Four: Cost
    Five: Cost
    Six: Optional[Cost]

    def get_mapping(self) -> Dict[int, Cost]:
        return {UpgradeTierCostIndex.first: self.One, UpgradeTierCostIndex.second: self.Two,
                UpgradeTierCostIndex.third: self.Three, UpgradeTierCostIndex.fourth: self.Four,
                UpgradeTierCostIndex.fifth: self.Five, UpgradeTierCostIndex.paragon: self.Six}


@dataclass
class UpgradesCost:
    top: UpgradeTierCost
    mid: UpgradeTierCost
    bottom: UpgradeTierCost

    def get_mapping(self) -> Dict[int, UpgradeTierCost]:
        return {UpgradeCostIndex.top: self.top, UpgradeCostIndex.middle: self.mid, UpgradeCostIndex.bottom: self.bottom}


@dataclass
class TowerCost:
    name: str
    base_cost: Cost
    upgrades: UpgradesCost
