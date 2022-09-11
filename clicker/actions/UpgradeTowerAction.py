import time

from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.consts import CLICK_DELAY
from clicker.money_extracter import get_amount_of_money
from common.cost.cost_parsing import TOWER_COSTS
from common.enums import Difficulty, UpgradeTier, TierLevel
from common.keymap import Keymap, UPGRADE_TIER_MAPPING
from common.tower import Tower


class UpgradeTowerAction(IAction):
    def __init__(self, ahk: AHK, difficulty: Difficulty, tower: Tower, tier: UpgradeTier):
        self._ahk = ahk
        self._difficulty = difficulty
        self._tower = tower
        self._tier = tier

    def act(self):

        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.click()
        time.sleep(CLICK_DELAY)
        self._ahk.key_press(UPGRADE_TIER_MAPPING[self._tier])
        time.sleep(CLICK_DELAY)
        self._ahk.send(Keymap.pause)  # close the window
        time.sleep(CLICK_DELAY)

        self._tower.tier_map[self._tier] += 1

    def can_act(self) -> bool:

        try:
            upgrade_price = TOWER_COSTS[self._tower.name].upgrades.get_mapping()[self._tier].get_mapping()[TierLevel(
                self._tower.tier_map[self._tier] + 1)].cost.get_mapping()[self._difficulty]
            money = get_amount_of_money()
            if money >= upgrade_price:
                print(f"Got {money}. Need: {upgrade_price}")
            return money >= upgrade_price
        except Exception as e:
            # TODO: add max tries
            pass
