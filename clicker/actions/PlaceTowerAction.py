from ahk import AHK

from clicker.actions.IAction import IAction
from common.cost.cost_parsing import TOWER_COSTS
from common.keymap import MonkeyKeymapMap
from clicker.money_extracter import get_amount_of_money
from common.tower import Tower


class PlaceTowerAction(IAction):

    def __init__(self, ahk: AHK, tower: Tower):
        self._ahk = ahk
        self._tower = tower

    def act(self):
        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.key_press(MonkeyKeymapMap[self._tower.name])
        self._ahk.click()

    def can_act(self) -> bool:
        # TODO: fix for every difficulty
        try:
            return get_amount_of_money() >= TOWER_COSTS[self._tower.name].base_cost.easy
        except Exception:
            # TODO: add max tries
            pass
