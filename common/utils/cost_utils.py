from common.game_classes.enums import Difficulty, UpgradeTier, TierLevel
from common.towers_info.game_info import TowersInfo


def get_base_cost(tower_name: str, difficulty: Difficulty) -> int:
    return TowersInfo()[tower_name].base_cost.get_mapping()[difficulty]


def get_upgrade_cost(tower_name: str, tier: UpgradeTier, upgrade_index: int, difficulty: Difficulty) -> int:
    tiers_cost = TowersInfo()[tower_name].upgrades.get_mapping()[tier]
    current_tier_costs = tiers_cost.get_mapping()[TierLevel(upgrade_index)]
    return current_tier_costs.cost.get_mapping()[difficulty]
