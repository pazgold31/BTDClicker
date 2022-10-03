import contextlib
from typing import Callable, Iterable

import pyautogui

from common.hotkeys import Hotkeys


class TowerPositionHotkeys:
    def __init__(self, observers: Iterable[Callable[[int, int], None]]):
        self._observers = observers

    def _record_tower(self):
        x, y = pyautogui.position()
        for observer in self._observers:
            observer(x, y)

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
