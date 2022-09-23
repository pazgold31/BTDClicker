import keyboard
from PySimpleGUI import Input
from ahk import AHK


class Hotkeys:
    def __init__(self, ahk: AHK, x_pos: Input, y_pos: Input):
        self._ahk = ahk
        self._x_pos = x_pos
        self._y_pos = y_pos
        keyboard.add_hotkey('ctrl + shift + r', self._record_tower)

    def _record_tower(self):
        x, y = self._ahk.mouse_position
        self._x_pos.update(x)
        self._y_pos.update(y)
