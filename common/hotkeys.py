from typing import Callable

import keyboard


class Hotkeys:
    def __init__(self):
        pass

    @staticmethod
    def add_hotkey(keys: str, callback: Callable):
        keyboard.add_hotkey(keys, callback)

    @staticmethod
    def remove_hotkey(callback: Callable):
        keyboard.remove_hotkey(callback)
