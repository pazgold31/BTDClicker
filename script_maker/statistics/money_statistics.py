import copy
from typing import Dict

from common.game_classes.enums import UpgradeTier
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry
from common.game_classes.tower import Tower
from common.utils.cost_utils import get_base_cost, get_upgrade_cost, get_hero_base_cost
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer


def calculate_cost(script_container: ScriptContainer, towers_container: TowersContainer, metadata: GameMetadata,
                   start: int = 0, end: int = None, sell_ratio: float = 0.7) -> int:
    tower_cost_map: Dict[int, int] = {tower_id: 0 for tower_id, _ in towers_container.items()}
    end = end if end is not None else len(script_container)

    new_towers_container = copy.deepcopy(towers_container)
    for _, single_tower in new_towers_container.items():
        if isinstance(single_tower, Tower):
            single_tower.tier_map = {j: 0 for j in UpgradeTier}

    for entry in script_container[start: end + 1]:
        if isinstance(entry, CreateTowerEntry):
            if entry.name == "Hero":
                tower_cost_map[entry.id] += get_hero_base_cost(hero_type=metadata.hero_type,
                                                               difficulty=metadata.difficulty)
            else:
                tower_cost_map[entry.id] += get_base_cost(tower_name=entry.name, difficulty=metadata.difficulty)
        elif isinstance(entry, UpgradeTowerEntry):
            tower = new_towers_container[entry.id]
            if not isinstance(tower, Tower):
                raise RuntimeError("Invalid tower")

            upgrade_price = get_upgrade_cost(tower_name=tower.name, tier=entry.tier, difficulty=metadata.difficulty,
                                             upgrade_index=(tower.tier_map[entry.tier] + 1))

            tower_cost_map[entry.id] += upgrade_price
            tower.tier_map[entry.tier] += 1
        elif isinstance(entry, SellTowerEntry):
            tower_cost_map[entry.id] *= (1 - sell_ratio)

    return sum(tower_cost_map.values())
