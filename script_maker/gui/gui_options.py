from typing import List, Callable

from common.game_classes.enums import Difficulty
from common.towers_info.game_info import HEROES_INFO, TOWERS_INFO
from common.towers_info.info_classes import TowerInfo


def get_tower_options(difficulty: Difficulty = Difficulty.easy, chosen_hero: str = None,
                      towers_filter: Callable[[TowerInfo], bool] = lambda x: True) -> List[str]:
    hero_str = "Hero" if not chosen_hero else \
        f"Hero | {chosen_hero}: {HEROES_INFO[chosen_hero].base_cost.get_mapping()[difficulty]}"
    return [hero_str] + \
           [f"{name}: {tower_info.base_cost.get_mapping()[difficulty]}$" for name, tower_info in TOWERS_INFO.items() if
            towers_filter(tower_info)]


def get_hero_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
    return [f"{name}: {hero_info.base_cost.get_mapping()[difficulty]}$" for name, hero_info in HEROES_INFO.items()]
