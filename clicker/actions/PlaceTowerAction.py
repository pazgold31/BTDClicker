from ahk import AHK

from clicker.actions.IAction import IAction
from common.enums import Difficulty
from common.cost.cost_parsing import TOWER_COSTS
from common.keymap import TOWER_KEY_MAP
from clicker.money_extracter import safe_get_amount_of_money
from common.tower import Tower


class PlaceTowerAction(IAction):

    def __init__(self, ahk: AHK, difficulty: Difficulty, tower: Tower):
        self._ahk = ahk
        self._difficulty = difficulty
        self._tower = tower

    def act(self):
        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.key_press(TOWER_KEY_MAP[self._tower.name])
        self._ahk.click()

    def can_act(self) -> bool:
        try:
            tower_price = TOWER_COSTS[self._tower.name].base_cost.get_mapping()[self._difficulty]
            return safe_get_amount_of_money() >= tower_price
        except Exception:
            # TODO: add max tries
            pass
