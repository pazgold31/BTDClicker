import itertools
from typing import Dict, List
import PySimpleGUI as sg

from common.script.script_dataclasses import IScriptEntry, GameMetadata
from common.tower import Tower
from script_maker.additional_tower_info import AdditionalTowerInfo
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_types import EventType, ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater


class GuiClass:
    def __init__(self, ):
        self._window = sg.Window(title="BTD Scripter", layout=get_layout())

        self._towers_list: Dict[int, Tower] = {}
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
        self._script: List[IScriptEntry] = []
        event, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=GuiParsers.parse_hero(values[GuiKeys.HeroListBox]))
        self._id_generator = itertools.count()

    def run(self):
        callback_map = self.get_callback_map()
        while True:
            event, values = self._window.read()

            if event in callback_map:
                callback_map[event](event, values)

            if event == sg.WIN_CLOSED:
                break

        self._window.close()

    def handle_change_difficulty(self, event: EventType, values: ValuesType):
        difficulty_str = values[GuiKeys.DifficultyListBox]
        self._metadata.difficulty = DIFFICULTY_MAP[difficulty_str]
        GuiUpdater.update_difficulty(window=self._window, values=values, metadata=self._metadata)

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty
        }


def main():
    gui_class = GuiClass()
    gui_class.run()


if __name__ == '__main__':
    main()
