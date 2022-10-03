from typing import Callable, List

from clicker.consts.keymap import TOWER_KEY_MAP
from common.game_classes.enums import UpgradeTier, Difficulty
from common.game_classes.tower import Hero, Tower
from common.towers_info.game_info import HEROES_INFO, TOWERS_INFO
from common.towers_info.info_classes import TowerInfo
from script_maker.script.towers_container import TowersContainer


class GuiFormatters:

    @staticmethod
    def format_tower_options(towers_filter: Callable[[TowerInfo], bool],
                             difficulty: Difficulty = Difficulty.easy,
                             chosen_hero: str = None) -> List[str]:
        hero_cost = HEROES_INFO[chosen_hero].base_cost.get_mapping()[difficulty]
        hero_prefix = f"Hero({TOWER_KEY_MAP['Hero']})"
        hero_str = hero_prefix if not chosen_hero else f"{hero_prefix} | {chosen_hero}: {hero_cost}"
        return [hero_str] + \
               [f"{name}({TOWER_KEY_MAP[name]}): {tower_info.base_cost.get_mapping()[difficulty]}$" for name, tower_info
                in TOWERS_INFO.items() if towers_filter(tower_info)]

    @staticmethod
    def format_hero_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
        return [f"{name}: {hero_info.base_cost.get_mapping()[difficulty]}$" for name, hero_info in HEROES_INFO.items()]

    @staticmethod
    def format_targeting(targeting: int):
        # TODO: support elite targeting and such
        targeting = targeting % 4
        return "First" if targeting == 0 else "Last" if targeting == 1 else "Close" if \
            targeting == 2 else "Strong"

    @staticmethod
    def format_existing_towers(towers_container: TowersContainer):
        output = []
        for tower_id, tower in towers_container.items():
            if isinstance(tower, Hero):
                output.append(f"{tower_id}: {tower.name} | x: {tower.x} y: {tower.y} |"
                              f"Targeting: {GuiFormatters.format_targeting(tower.targeting)} | "
                              f"S.Targeting: {tower.s_targeting}"
                              f"{' SOLD' if tower.sold else ''}")
            elif isinstance(tower, Tower):
                output.append(
                    f"{tower_id}: {tower.name} | x: {tower.x} y: {tower.y} | {tower.tier_map[UpgradeTier.top]}-"
                    f"{tower.tier_map[UpgradeTier.middle]}-{tower.tier_map[UpgradeTier.bottom]} | "
                    f"Targeting: {GuiFormatters.format_targeting(tower.targeting)} | "
                    f"S.Targeting: {tower.s_targeting}"
                    f"{' SOLD' if tower.sold else ''}")
            else:
                raise RuntimeError

        return output
