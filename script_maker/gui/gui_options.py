from typing import Callable

from common.game_classes.enums import Difficulty
from common.towers_info.game_info import g_heroes_info, g_towers_info
from common.towers_info.info_classes import TowerInfo
from common.utils.cost_utils import get_base_cost


def get_tower_options(towers_filter: Callable[[TowerInfo], bool],
                      difficulty: Difficulty = Difficulty.easy,
                      chosen_hero: str = None) -> list[str]:
    hero_str = "Hero" if not chosen_hero else \
        f"Hero | {chosen_hero}: {g_heroes_info[chosen_hero].base_cost.get_mapping()[difficulty]}"
    return [hero_str] + \
           [f"{name}: {get_base_cost(tower_name=name, difficulty=difficulty)}$" for name, tower_info in
            g_towers_info.items() if towers_filter(tower_info)]


def get_hero_options(difficulty: Difficulty = Difficulty.easy) -> list[str]:
    return [f"{name}: {get_base_cost(tower_name=name, difficulty=difficulty)}$" for name, hero_info in
            g_heroes_info.items()]
