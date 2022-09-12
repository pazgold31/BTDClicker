import PySimpleGUI as sg

from common.script.script_dataclasses import GameMetadata
from script_maker.gui.gui_types import ValuesType
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_tower_options, get_hero_options


class GuiUpdater:
    @staticmethod
    def update_difficulty(window: sg.Window, values: ValuesType, metadata: GameMetadata):
        window[GuiKeys.TowerTypesListBox].update(
            get_tower_options(difficulty=metadata.difficulty, chosen_hero=metadata.hero_type), )
        selected_hero_index = window[GuiKeys.HeroListBox].Values.index(values[GuiKeys.HeroListBox])
        hero_options = get_hero_options(difficulty=metadata.difficulty)
        window[GuiKeys.HeroListBox].update(values=hero_options, value=hero_options[selected_hero_index])
