from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.money_extracter import get_amount_of_money
from common.cost.game_costs import HERO_COSTS
from common.game_classes.enums import Difficulty
from clicker.consts.keymap import Keymap
from common.game_classes.tower import BaseTower


class PlaceHeroAction(IAction):

    def __init__(self, ahk: AHK, difficulty: Difficulty, hero: BaseTower):
        self._ahk = ahk
        self._difficulty = difficulty
        self._hero = hero

    def act(self):
        self._ahk.mouse_position = (self._hero.x, self._hero.y)
        self._ahk.key_press(Keymap.hero)
        self._ahk.click()

    def can_act(self) -> bool:
        # noinspection PyBroadException
        try:
            tower_price = HERO_COSTS[self._hero.name].base_cost.get_mapping()[self._difficulty]
            return get_amount_of_money() >= tower_price
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Place {self._hero.name} at {self._hero.x}:{self._hero.y}"
