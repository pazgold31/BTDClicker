import itertools
from typing import Dict, Callable, List, Any
import PySimpleGUI as sg

from common.enums import Difficulty
from common.script.script_dataclasses import IScriptEntry, GameMetadata
from common.tower import Tower
from script_maker.additional_tower_info import AdditionalTowerInfo
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP

CallbackMethod = Callable[[Dict[str, Any], List[Any]], None]


class GuiClass:
    def __init__(self, ):
        self._window = sg.Window(title="BTD Scripter", layout=get_layout())

        self._towers_list: Dict[int, Tower] = {}
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
        self._script: List[IScriptEntry] = []
        event, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=values[GuiKeys.HeroListBox])
        self._id_generator = itertools.count()

    def run(self):
        while True:
            event, values = self._window.read()

            if event == sg.WIN_CLOSED:
                break

        self._window.close()

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {}


def main():
    gui_class = GuiClass()
    gui_class.run()


if __name__ == '__main__':
    main()
