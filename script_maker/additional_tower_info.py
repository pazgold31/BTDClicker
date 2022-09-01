from dataclasses import dataclass
from typing import Dict


@dataclass
class AdditionalTowerInfo:
    sold: bool = False
    targeting: int = 0
    s_targeting: int = 0


def get_additional_information(tower_id: int, d: Dict[int, AdditionalTowerInfo]):
    if tower_id not in d:
        d[tower_id] = AdditionalTowerInfo()

    return d[tower_id]
