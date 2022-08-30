import time

from ahk import AHK

from clicker.actions.IAction import IAction
from common.cost.cost_parsing import TOWER_COSTS
from common.keymap import Keymap
from clicker.money_extracter import get_amount_of_money
from common.tower import Tower


class UpgradeTowerAction(IAction):
    def __init__(self, ahk: AHK, tower: Tower, tier: int):
        self._ahk = ahk
        self._tower = tower
        self._tier = tier

    def act(self) -> Tower:
        key = Keymap.UpgradeTop if self._tier == 0 else Keymap.UpgradeMiddle if self._tier == 1 else \
            Keymap.UpgradeBottom if self._tier == 2 else -1
        if key == -1:
            raise RuntimeError("Invalid tier")

        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.click()
        time.sleep(0.2)
        self._ahk.key_press(key)
        time.sleep(0.2)
        self._ahk.send(Keymap.Pause)
        time.sleep(0.2)

    def can_act(self) -> bool:
        # TODO: fix for every difficulty

        try:
            m = {1: self._tower.top, 2: self._tower.middle, 3: self._tower.bottom}
            upgrade_cost = TOWER_COSTS[self._tower.name].upgrades.get_mapping()[self._tier + 1].get_mapping()[
                m[self._tier + 1] + 1].cost.get_mapping()[1]
            return get_amount_of_money() >= upgrade_cost
        except Exception as e:
            # TODO: add max tries
            print(e)
