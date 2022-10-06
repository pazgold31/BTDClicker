import time

from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.consts.keymap import Keymap, UPGRADE_TIER_MAPPING
from clicker.consts.timing_consts import CLICK_DELAY
from clicker.money_extracter import get_amount_of_money
from common.utils.cost_utils import get_upgrade_cost
from common.game_classes.enums import Difficulty, UpgradeTier
from common.game_classes.tower import Tower


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

        # noinspection PyBroadException
        try:
            upgrade_price = get_upgrade_cost(tower_name=self._tower.name, tier=self._tier,
                                             upgrade_index=(self._tower.tier_map[self._tier] + 1),
                                             difficulty=self._difficulty)
            money = get_amount_of_money()
            if money >= upgrade_price:
                print(f"Got {money}. Need: {upgrade_price}")
            return money >= upgrade_price
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Upgrade {self._tower.name} tier {self._tier.name}"
