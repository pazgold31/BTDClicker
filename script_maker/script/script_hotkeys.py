from PySimpleGUI import Input
import pyautogui

from common.hotkeys import Hotkeys


class ScriptHotkeys:
    def __init__(self, x_pos: Input, y_pos: Input):
        self._x_pos = x_pos
        self._y_pos = y_pos

    def _record_tower(self):
        x, y = pyautogui.position()
        self._x_pos.update(x)
        self._y_pos.update(y)

    def record_towers_position(self):
        Hotkeys.add_hotkey('ctrl + shift + r', self._record_tower)

    def stop_recording_towers_position(self):
        Hotkeys.remove_hotkey(self._record_tower)

    def __enter__(self):
        self.record_towers_position()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_recording_towers_position()