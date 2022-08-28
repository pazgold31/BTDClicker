import keyboard
from ahk import AHK


class Hotkeys:
    def __init__(self, ahk: AHK):
        self._ahk = ahk
        keyboard.add_hotkey('ctrl + shift + r', self._record_tower)

    def _record_tower(self):
        print(f"Mouse at: {self._ahk.mouse_position}")
