import sys
from typing import Optional

from PySimpleGUI import Listbox

from clicker.consts.keymap import TOWER_KEY_MAP
from common.hotkeys import Hotkeys
from script_maker.gui.gui_controls_utils import GuiControlsUtils


class TowerTypesHotkeys:
    def __init__(self, tower_types: Optional[Listbox] = None):
        self._tower_types = tower_types

    def _record_towers_hotkeys(self, tower_name: str):
        if not self._tower_types:
            raise RuntimeError

        list_values = self._tower_types.get_list_values()
        try:
            tower_list_row = [i for i in list_values if tower_name in i][0]
        except IndexError:
            return

        GuiControlsUtils.update_listbox_item(listbox=self._tower_types, set_to_index=list_values.index(tower_list_row))

    def record_towers_hotkeys(self):
        if sys.gettrace():
            # Since the hotkeys are single letters. You can't debug when the key binds are active.
            print("Debugging is present, skipping hotkeys for towers")
            return

        for tower_name, tower_hotkey in TOWER_KEY_MAP.items():
            Hotkeys.add_hotkey(tower_hotkey, lambda i=tower_name: self._record_towers_hotkeys(tower_name=i))
