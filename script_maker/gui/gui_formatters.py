from typing import Callable, List

from clicker.consts.keymap import TOWER_KEY_MAP
from common.game_classes.enums import UpgradeTier, Difficulty
from common.game_classes.tower import Hero, Tower, BaseTower
from common.towers_info.game_info import g_towers_info, g_heroes_info
from common.towers_info.info_classes import TowerInfo
from common.utils.cost_utils import get_base_cost
from script_maker.script.towers_container import TowersContainer


class GuiFormatters:

    @staticmethod
    def format_tower_options(towers_filter: Callable[[TowerInfo], bool],
                             difficulty: Difficulty = Difficulty.easy,
                             chosen_hero: str = None) -> List[str]:
        hero_cost = g_heroes_info[chosen_hero].base_cost.get_mapping()[difficulty]
        hero_prefix = f"Hero({TOWER_KEY_MAP['Hero']})"
        hero_str = hero_prefix if not chosen_hero else f"{hero_prefix} | {chosen_hero}: {hero_cost}"
        return [hero_str] + \
               [f"{name}({TOWER_KEY_MAP[name]}): {get_base_cost(tower_name=name, difficulty=difficulty)}$" for
                name, tower_info in g_towers_info.items() if towers_filter(tower_info)]

    @staticmethod
    def format_hero_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
        return [f"{name}: {hero_info.base_cost.get_mapping()[difficulty]}$" for name, hero_info in
                g_heroes_info.items()]

    @staticmethod
    def format_targeting(targeting: int) -> str:
        # TODO: support elite targeting and such
        targeting = targeting % 4
        return "First" if targeting == 0 else "Last" if targeting == 1 else "Close" if \
            targeting == 2 else "Strong"

    @staticmethod
    def format_tower_tiers(tower: Tower) -> str:
        tm = tower.tier_map
        return f"{tm[UpgradeTier.top]}-{tm[UpgradeTier.middle]}-{tm[UpgradeTier.bottom]}"

    @staticmethod
    def format_tower_position(tower: BaseTower) -> str:
        return f"x: {tower.x} y: {tower.y}"

    @staticmethod
    def format_tower_targeting(tower: BaseTower) -> str:
        return f"Targeting: {GuiFormatters.format_targeting(tower.targeting)} | S.Targeting: {tower.s_targeting}"

    @staticmethod
    def format_tower_sold_status(tower: BaseTower) -> str:
        return "SOLD" if tower.sold else ""

    @staticmethod
    def format_existing_towers(towers_container: TowersContainer) -> List[str]:
        output = []
        for tower_id, tower in towers_container.items():
            if isinstance(tower, Hero):
                output.append(f"{tower_id}: Hero | {GuiFormatters.format_tower_position(tower)} |"
                              f"{GuiFormatters.format_tower_targeting(tower)} | "
                              f"{GuiFormatters.format_tower_sold_status(tower)}")
            elif isinstance(tower, Tower):
                output.append(f"{tower_id}: {tower.name} | {GuiFormatters.format_tower_position(tower)} | "
                              f"{GuiFormatters.format_tower_tiers(tower)} | "
                              f"{GuiFormatters.format_tower_targeting(tower)} | "
                              f"{GuiFormatters.format_tower_sold_status(tower)}")
            else:
                raise RuntimeError

        return output
