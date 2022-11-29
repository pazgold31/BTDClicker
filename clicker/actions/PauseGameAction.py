import time

from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.clicker_state import g_clicker_state
from clicker.consts.keymap import Keymap
from clicker.consts.timing_consts import CLICK_DELAY


class PauseGameAction(IAction):

    def __init__(self, ahk: AHK):
        self._ahk = ahk

    def act(self):
        self._ahk.send(Keymap.pause)
        time.sleep(CLICK_DELAY)
        g_clicker_state.stop()

    def can_act(self) -> bool:
        return True

    def get_action_message(self) -> str:
        return f"Paused game"
