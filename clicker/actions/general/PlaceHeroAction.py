from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.consts.keymap import Keymap
from clicker.money_extracter import get_amount_of_money
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.tower import BaseTower
from common.towers_info.game_info import g_heroes_info


class PlaceHeroAction(IAction):

    def __init__(self, ahk: AHK, metadata: GameMetadata, hero: BaseTower):
        self._ahk = ahk
        self._metadata = metadata
        self._hero = hero

    def act(self):
        self._ahk.mouse_position = (self._hero.x, self._hero.y)
        self._ahk.key_press(Keymap.hero)
        self._ahk.click()

    def can_act(self) -> bool:
        # noinspection PyBroadException
        try:
            tower_price = g_heroes_info[self._metadata.hero_type].base_cost.get_mapping()[self._metadata.difficulty]
            return get_amount_of_money() >= tower_price
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Place Hero({self._metadata.hero_type}) at {self._hero.x}:{self._hero.y}"
