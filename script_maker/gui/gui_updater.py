import PySimpleGUI as sg

from common.script.script_dataclasses import GameMetadata
from script_maker.gui.gui_types import ValuesType
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_tower_options, get_hero_options


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata):
        self._window = window
        self._metadata = metadata

    def update_difficulty(self, values: ValuesType):
        self._window[GuiKeys.TowerTypesListBox].update(
            get_tower_options(difficulty=self._metadata.difficulty, chosen_hero=self._metadata.hero_type), )
        selected_hero_index = self._window[GuiKeys.HeroListBox].Values.index(values[GuiKeys.HeroListBox])
        hero_options = get_hero_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.HeroListBox].update(values=hero_options, value=hero_options[selected_hero_index])

    def update_hero(self, metadata: GameMetadata):
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(difficulty=metadata.difficulty,
                                                                         chosen_hero=metadata.hero_type), )

    def update_selected_tower(self, values: ValuesType, selected_tower_text: str):
        selected_tower_index = self._window[GuiKeys.TowerTypesListBox].Values.index(
            values[GuiKeys.TowerTypesListBox][0])
        tower_options = get_tower_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.TowerTypesListBox].update(None, tower_options[selected_tower_index])
        self._window[GuiKeys.NewTowerTypeInput].update(selected_tower_text, )
