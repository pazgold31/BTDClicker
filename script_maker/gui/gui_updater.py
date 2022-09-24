# noinspection PyPep8Naming
import tkinter
from typing import Callable

import PySimpleGUI as sg

from common.game_classes.script.script_dataclasses import GameMetadata, CreateTowerEntry, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry
from common.towers_info.game_info import HEROES_INFO
from common.towers_info.info_classes import TowerInfo
from script_maker.gui.gui_controls_utils import get_selected_index_for_list_box
from script_maker.gui.gui_formatters import GuiFormatters
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import DIFFICULTY_MAP
from script_maker.gui.gui_options import get_tower_options, get_hero_options
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.towers_container import TowersContainer


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata):
        self._window = window
        self._metadata = metadata

    def update_difficulty(self):
        self._window[GuiKeys.TowerTypesListBox].update(
            get_tower_options(difficulty=self._metadata.difficulty, chosen_hero=self._metadata.hero_type), )
        selected_hero_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.HeroCombo)
        hero_options = get_hero_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.HeroCombo].update(values=hero_options, value=hero_options[selected_hero_index])

    def update_tower_types(self, towers_filter: Callable[[TowerInfo], bool]):
        self._window[GuiKeys.TowerTypesListBox].update(
            values=get_tower_options(difficulty=self._metadata.difficulty,
                                     chosen_hero=self._metadata.hero_type,
                                     towers_filter=towers_filter))

    def update_selected_difficulty(self):
        self._window[GuiKeys.DifficultyListBox].update(
            value={v: k for k, v in DIFFICULTY_MAP.items()}[self._metadata.difficulty])

    def update_hero(self):
        self._window[GuiKeys.TowerTypesListBox].update(values=get_tower_options(difficulty=self._metadata.difficulty,
                                                                                chosen_hero=self._metadata.hero_type))

    def update_selected_hero(self):
        hero_cost = HEROES_INFO[self._metadata.hero_type].base_cost.get_mapping()[self._metadata.difficulty]
        hero_value = f"{self._metadata.hero_type}: {hero_cost}$"
        self._window[GuiKeys.HeroCombo].update(value=hero_value)

    def update_selected_tower_type(self, selected_tower_text: str):
        selected_tower_index = get_selected_index_for_list_box(window=self._window,
                                                               key=GuiKeys.TowerTypesListBox)
        tower_options = get_tower_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.TowerTypesListBox].update(None, tower_options[selected_tower_index])
        self._window[GuiKeys.NewTowerTypeInput].update(selected_tower_text, )

    def update_selected_existing_tower(self, is_hero: bool):
        self._window[GuiKeys.TopUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.MiddleUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.BottomUpgradeButton].update(disabled=is_hero)

    def update_existing_towers(self, towers_container: TowersContainer):
        list_box = self._window[GuiKeys.ExistingTowersListBox]
        try:
            selected_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ExistingTowersListBox)
        except IndexError:
            selected_index = None

        list_box_items = GuiFormatters.format_existing_towers(towers_container)
        list_box.update(values=list_box_items, set_to_index=selected_index)
        for i in range(len(list_box_items)):
            listbox_widget: tkinter.Listbox = list_box.widget
            listbox_widget.itemconfig(i, bg=towers_container.get_tower_color(tower_id=i))

    def update_script_box(self, activity_container: ActivityContainer, selected_index: int = None):
        output = []
        for action in activity_container.script_container:
            if isinstance(action, CreateTowerEntry):
                output.append(f"Create: {action.name}({action.id}) | X: {action.x} Y: {action.y}")
            elif isinstance(action, UpgradeTowerEntry):
                output.append(f"Upgrade: ({action.id}) | tier: {action.tier}")
            elif isinstance(action, SellTowerEntry):
                output.append(f"Sell: ({action.id})")
            elif isinstance(action, ChangeTargetingEntry):
                output.append(f"Change targeting: ({action.id})")
            elif isinstance(action, ChangeSpecialTargetingEntry):
                output.append(f"Change special targeting: ({action.id})")

        try:
            selected_index = selected_index if selected_index is not None else get_selected_index_for_list_box(
                window=self._window, key=GuiKeys.ScriptBox)
        except IndexError:
            selected_index = None

        list_box = self._window[GuiKeys.ScriptBox]
        list_box.update(values=output, set_to_index=selected_index)
        for i, script_entry in enumerate(activity_container.script_container):
            listbox_widget: tkinter.Listbox = list_box.widget
            listbox_widget.itemconfig(i,
                                      bg=activity_container.towers_container.get_tower_color(tower_id=script_entry.id))

        if selected_index is not None:
            self._window[GuiKeys.ScriptBox].Widget.see(selected_index)

    def update_existing_towers_and_script(self, activity_container: ActivityContainer,
                                          selected_script_index: int = None):
        self.update_existing_towers(towers_container=activity_container.towers_container)
        self.update_script_box(activity_container=activity_container, selected_index=selected_script_index)
