import re

from common.game_classes.enums import UpgradeTier
from common.game_classes.tower import Tower


def is_tier_upgradeable(tower: Tower, tier: UpgradeTier) -> bool:
    def get_tier_value(current_tier: UpgradeTier) -> str:
        return f"{tower.tier_map[current_tier] + (1 if tier == current_tier else 0)}"

    str_representation = f"{get_tier_value(UpgradeTier.top)}" \
                         f"{get_tier_value(UpgradeTier.middle)}" \
                         f"{get_tier_value(UpgradeTier.bottom)}"
    return is_tiers_text_valid(tiers_text=str_representation)


def is_tiers_text_valid(tiers_text: str) -> bool:
    """
    Checks if a string representation of towers tiers(e.g. 103, 402 etc) is valid.
    """
    return bool(re.match(r"(?=.*0)(?=^[0-2]*[3-5]?[0-2]*$)(?=^[0-5]{3}$)", tiers_text))
