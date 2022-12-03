from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.consts.keymap import TOWER_KEY_MAP
from clicker.money_extracter import get_amount_of_money
from common.game_classes.enums import Difficulty
from common.game_classes.tower import Tower
from common.utils.cost_utils import get_base_cost


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
        # noinspection PyBroadException
        try:
            tower_price = get_base_cost(tower_name=self._tower.name, difficulty=self._difficulty)
            money = get_amount_of_money()
            if money >= tower_price:
                print(f"Got {money}. Need: {tower_price}")
                return True

            return False
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Place {self._tower.name} at {self._tower.x}:{self._tower.y}"
