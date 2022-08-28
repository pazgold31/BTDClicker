from ahk import AHK

from actions.IAction import IAction
from cost_parser import TOWER_COSTS
from keymap import Keymap
from money_extracter import get_amount_of_money
from tower import Tower


class UpgradeTowerActions(IAction):
    def __init__(self, ahk: AHK, tower: Tower, tier: int):
        self._ahk = ahk
        self._tower = tower
        self._tier = tier

    def act(self) -> Tower:
        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        key = Keymap.UpgradeTop if self._tier == 0 else Keymap.UpgradeMiddle if self._tier == 1 else \
            Keymap.UpgradeBottom if self._tier == 2 else -1
        if key == -1:
            raise RuntimeError("Invalid tier")

        self._ahk.key_press(key)

    def can_act(self) -> bool:
        # TODO: fix for every difficulty
        return get_amount_of_money() == TOWER_COSTS[self._tower.name].base_cost.easy
