import sys
from typing import Callable, Iterable

from clicker.consts.keymap import TOWER_KEY_MAP
from common.hotkeys import Hotkeys


class TowerTypesHotkeys:
    def __init__(self, observers: Iterable[Callable[[str], None]]):
        self._observers = observers

    def _hotkey_callback(self, tower_name: str):

        for observer in self._observers:
            observer(tower_name)

    def record_towers_hotkeys(self):
        if sys.gettrace():
            # Since the hotkeys are single letters. You can't debug when the key binds are active.
            print("Debugging is present, skipping hotkeys for towers")
            return

        for tower_name, tower_hotkey in TOWER_KEY_MAP.items():
            Hotkeys.add_hotkey(tower_hotkey, lambda i=tower_name: self._hotkey_callback(tower_name=i))
