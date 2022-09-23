from dataclasses import dataclass


@dataclass
class AdditionalTowerInfo:
    sold: bool = False
    targeting: int = 0
    s_targeting: int = 0
