import time

from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.consts import CLICK_DELAY
from common.keymap import Keymap
from common.tower import Tower


class SellTowerAction(IAction):

    def __init__(self, ahk: AHK, tower: Tower):
        self._ahk = ahk
        self._tower = tower

    def act(self):
        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.click()
        time.sleep(CLICK_DELAY)
        self._ahk.send(Keymap.sell)
        time.sleep(CLICK_DELAY)

    def can_act(self) -> bool:
        return True
