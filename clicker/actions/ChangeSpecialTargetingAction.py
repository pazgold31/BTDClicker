import time

from ahk import AHK

from clicker.actions.IAction import IAction
from common.keymap import Keymap
from common.tower import Tower


class ChangeSpecialTargetingAction(IAction):

    def __init__(self, ahk: AHK, tower: Tower):
        self._ahk = ahk
        self._tower = tower

    def act(self):
        self._ahk.mouse_position = (self._tower.x, self._tower.y)
        self._ahk.click()
        time.sleep(0.2)
        self._ahk.send(Keymap.change_special_targeting)
        time.sleep(0.1)
        self._ahk.send(Keymap.pause)  # close the window
        time.sleep(0.1)

    def can_act(self) -> bool:
        return True
