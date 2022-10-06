from typing import Callable, Iterable

from common.hotkeys import Hotkeys
from script_maker.hotkey_map import ScriptHotkeyMap


class SaveTowerHotkeys:
    def __init__(self, observers: Iterable[Callable[[], None]]):
        self._observers = observers

    def _hotkey_callback(self):
        for observer in self._observers:
            observer()

    def record_towers_saving(self):
        Hotkeys.add_hotkey(ScriptHotkeyMap.save_tower, self._hotkey_callback)
