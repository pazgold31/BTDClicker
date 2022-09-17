from typing import Dict

from common.cost.cost_classes import HeroCost, TowerCost
from common.cost.cost_parsing import get_hero_costs, get_tower_costs

HERO_COSTS: Dict[str, HeroCost] = get_hero_costs()
TOWER_COSTS: Dict[str, TowerCost] = get_tower_costs()
