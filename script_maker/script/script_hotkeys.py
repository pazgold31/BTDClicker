import contextlib

import pyautogui
from PySimpleGUI import Input, Listbox

from clicker.consts.keymap import TOWER_KEY_MAP
from common.hotkeys import Hotkeys


class ScriptHotkeys:
    def __init__(self, x_pos: Input, y_pos: Input, tower_types: Listbox):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._tower_types = tower_types

    def _record_tower(self):
        x, y = pyautogui.position()
        self._x_pos.update(x)
        self._y_pos.update(y)

    def _record_towers_hotkeys(self, tower_name: str):
        list_values = self._tower_types.get_list_values()
        try:
            tower_list_row = [i for i in list_values if tower_name in i][0]
        except IndexError:
            return

        self._tower_types.update(None, set_to_index=list_values.index(tower_list_row))

    def record_towers_hotkeys(self):
        for tower_name, tower_hotkey in TOWER_KEY_MAP.items():
            Hotkeys.add_hotkey(tower_hotkey, lambda i=tower_name: self._record_towers_hotkeys(tower_name=i))

    def record_towers_position(self):
        Hotkeys.add_hotkey('ctrl + shift + r', self._record_tower)

    def stop_recording_towers_position(self):
        Hotkeys.remove_hotkey(self._record_tower)

    @contextlib.contextmanager
    def pause_capture(self):
        try:
            self.stop_recording_towers_position()
            yield
        finally:
            self.record_towers_position()

    @contextlib.contextmanager
    def capture_positions(self):
        try:
            self.record_towers_position()
            yield
        finally:
            self.stop_recording_towers_position()
