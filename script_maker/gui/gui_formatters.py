from common.game_classes.enums import UpgradeTier
from common.game_classes.tower import Hero, Tower
from script_maker.script.towers_container import TowersContainer


class GuiFormatters:
    @staticmethod
    def format_targeting(targeting: int):
        # TODO: support elite targeting and such
        targeting = targeting % 4
        return "First" if targeting == 0 else "Last" if targeting == 1 else "Close" if \
            targeting == 2 else "Strong"

    @staticmethod
    def format_existing_towers(towers_container: TowersContainer):
        output = []
        for tower_id, tower, additional_tower_information in towers_container.iter_with_additional_information():
            if isinstance(tower, Hero):
                output.append(f"{tower_id}: {tower.name} | x: {tower.x} y: {tower.y} |"
                              f"Targeting: {GuiFormatters.format_targeting(additional_tower_information.targeting)} | "
                              f"S.Targeting: {additional_tower_information.s_targeting}"
                              f"{' SOLD' if additional_tower_information.sold else ''}")
            elif isinstance(tower, Tower):
                output.append(
                    f"{tower_id}: {tower.name} | x: {tower.x} y: {tower.y} | {tower.tier_map[UpgradeTier.top]}-"
                    f"{tower.tier_map[UpgradeTier.middle]}-{tower.tier_map[UpgradeTier.bottom]} | "
                    f"Targeting: {GuiFormatters.format_targeting(additional_tower_information.targeting)} | "
                    f"S.Targeting: {additional_tower_information.s_targeting}"
                    f"{' SOLD' if additional_tower_information.sold else ''}")
            else:
                raise RuntimeError

        return output
