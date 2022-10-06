from typing import Dict

from common.cost_utils import get_base_cost, get_upgrade_cost
from common.game_classes.enums import Difficulty
from common.game_classes.script.script_dataclasses import CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry
from common.game_classes.tower import Tower
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer


def calculate_cost(script_container: ScriptContainer, towers_container: TowersContainer, difficulty: Difficulty,
                   start: int = 0, end: int = None, sell_ratio: float = 0.7) -> int:
    tower_cost_map: Dict[int, int] = {tower_id: 0 for tower_id, _ in towers_container.items()}
    end = end if end is not None else len(script_container)

    tower_tier_map: Dict[int, Tower] = {tower_id: Tower(name=tower.name, x=tower.x, y=tower.y) for tower_id, tower in
                                        towers_container.items()}

    for entry in script_container[start: end + 1]:
        if isinstance(entry, CreateTowerEntry):
            tower_cost_map[entry.id] += get_base_cost(tower_name=entry.name, difficulty=difficulty)
        elif isinstance(entry, UpgradeTowerEntry):
            tower = tower_tier_map[entry.id]

            upgrade_price = get_upgrade_cost(tower_name=tower.name, tier=entry.tier, difficulty=difficulty,
                                             upgrade_index=(tower.tier_map[entry.tier] + 1))

            tower_cost_map[entry.id] += upgrade_price
            tower.tier_map[entry.tier] += 1
        elif isinstance(entry, SellTowerEntry):
            tower_cost_map[entry.id] *= (1 - sell_ratio)

    return sum(tower_cost_map.values())