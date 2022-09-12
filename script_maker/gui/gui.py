from typing import List

from common.cost.cost_parsing import TOWER_COSTS, HERO_COSTS
from common.enums import Difficulty

DIFFICULTY_MAP = {"easy": Difficulty.easy, "medium": Difficulty.medium,
                  "hard": Difficulty.hard, "chimps": Difficulty.chimps}


def get_tower_options(difficulty: Difficulty = Difficulty.easy, chosen_hero: str = None) -> List[str]:
    hero_str = "Hero" if not chosen_hero else \
        f"Hero | {chosen_hero}: {HERO_COSTS[chosen_hero].base_cost.get_mapping()[difficulty]}"
    return [hero_str] + \
           [f"{name}: {cost.base_cost.get_mapping()[difficulty]}$" for name, cost in TOWER_COSTS.items()]


def get_hero_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
    return [f"{name}: {cost.base_cost.get_mapping()[difficulty]}$" for name, cost in HERO_COSTS.items()]
