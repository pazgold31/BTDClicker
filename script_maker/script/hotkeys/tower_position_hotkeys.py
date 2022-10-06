import contextlib
from typing import Callable, Iterable

import pyautogui

from common.hotkeys import Hotkeys
from script_maker.hotkey_map import ScriptHotkeyMap


class TowerPositionHotkeys:
    def __init__(self, observers: Iterable[Callable[[int, int], None]]):
        self._observers = observers

    def _hotkey_callback(self):
        x, y = pyautogui.position()
        for observer in self._observers:
            observer(x, y)

    def record_towers_position(self):
        Hotkeys.add_hotkey(ScriptHotkeyMap.capture_tower_position, self._hotkey_callback)

    def stop_recording_towers_position(self):
        Hotkeys.remove_hotkey(self._hotkey_callback)

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
