# noinspection PyPep8Naming
from typing import Callable, Union, List

# noinspection PyPep8Naming
import PySimpleGUI as sg

from common.game_classes.script.script_dataclasses import GameMetadata, CreateTowerEntry, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry, PauseEntry, WaitForMoneyEntry, \
    ITowerModifyingScriptEntry
from common.towers_info.game_info import HEROES_INFO
from common.towers_info.info_classes import TowerInfo
from script_maker.gui.gui_colors import GLOBAL_ENTRIES_COLOR
from script_maker.gui.gui_controls_utils import GuiControlsUtils
from script_maker.gui.gui_formatters import GuiFormatters
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import DIFFICULTY_MAP
from script_maker.gui.gui_options import get_tower_options, get_hero_options
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.towers_container import TowersContainer


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata, controls_utils: GuiControlsUtils):
        self._window = window
        self._metadata = metadata
        self._controls_utils = controls_utils

    def update_difficulty(self):
        self._window[GuiKeys.TowerTypesListBox].update(
            get_tower_options(towers_filter=lambda _: True, difficulty=self._metadata.difficulty,
                              chosen_hero=self._metadata.hero_type), )
        selected_hero_index = self._controls_utils.get_selected_index_from_combo(key=GuiKeys.HeroCombo)
        hero_options = get_hero_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.HeroCombo].update(values=hero_options, value=hero_options[selected_hero_index])

    def update_tower_types(self, towers_filter: Callable[[TowerInfo], bool], selected_value: str):
        tower_options = get_tower_options(difficulty=self._metadata.difficulty,
                                          chosen_hero=self._metadata.hero_type,
                                          towers_filter=towers_filter)
        selected_index = None
        if selected_value in tower_options:
            selected_index = tower_options.index(selected_value)

        list_box = self._window[GuiKeys.TowerTypesListBox]
        list_box.update(values=tower_options, set_to_index=selected_index)
        self._controls_utils.add_alternating_colors(listbox_widget=list_box.widget)

    def update_selected_difficulty(self):
        self._window[GuiKeys.DifficultyListBox].update(
            value={v: k for k, v in DIFFICULTY_MAP.items()}[self._metadata.difficulty])

    def update_hero(self):
        self._window[GuiKeys.TowerTypesListBox].update(values=get_tower_options(difficulty=self._metadata.difficulty,
                                                                                chosen_hero=self._metadata.hero_type,
                                                                                towers_filter=lambda _: True), )

    def update_selected_hero(self):
        hero_cost = HEROES_INFO[self._metadata.hero_type].base_cost.get_mapping()[self._metadata.difficulty]
        hero_value = f"{self._metadata.hero_type}: {hero_cost}$"
        self._window[GuiKeys.HeroCombo].update(value=hero_value)

    def update_selected_tower_type(self, selected_tower_text: str):
        try:
            selected_tower_index = self._controls_utils.get_first_selected_index_for_list_box(
                key=GuiKeys.TowerTypesListBox)
        except ValueError:
            self._window[GuiKeys.TowerTypesListBox].update(None, set_to_index=[])
            raise

        self._window[GuiKeys.TowerTypesListBox].update(None, set_to_index=selected_tower_index)
        self._window[GuiKeys.NewTowerTypeInput].update(selected_tower_text, )

    def update_selected_existing_tower(self, is_hero: bool):
        self._window[GuiKeys.TopUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.MiddleUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.BottomUpgradeButton].update(disabled=is_hero)

    def update_existing_towers(self, towers_container: TowersContainer):
        list_box = self._window[GuiKeys.ExistingTowersListBox]
        selected_indexes = self._controls_utils.get_selected_indexes_for_list_box(key=GuiKeys.ExistingTowersListBox)

        list_box_items = GuiFormatters.format_existing_towers(towers_container)
        list_box.update(values=list_box_items, set_to_index=selected_indexes)
        for i in range(len(list_box_items)):
            self._controls_utils.change_cell_color(listbox_widget=list_box.widget, index=i,
                                                   color=towers_container.get_tower_color(tower_id=i))

    def update_script_box(self, activity_container: ActivityContainer, selected_index: Union[int, List[int]] = None):
        output = []
        for action in activity_container.script_container:
            if isinstance(action, PauseEntry):
                output.append("Pause game.")
            if isinstance(action, WaitForMoneyEntry):
                output.append(f"Wait for {action.amount}$")
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

        list_box = self._window[GuiKeys.ScriptBox]
        list_box.update(values=output, set_to_index=selected_index)
        for i, script_entry in enumerate(activity_container.script_container):
            if isinstance(script_entry, ITowerModifyingScriptEntry):
                self._controls_utils.change_cell_color(listbox_widget=list_box.widget, index=i,
                                                       color=activity_container.towers_container.get_tower_color(
                                                           tower_id=script_entry.id))
            else:
                self._controls_utils.change_cell_color(listbox_widget=list_box.widget, index=i,
                                                       color=GLOBAL_ENTRIES_COLOR)

        if selected_index is not None:
            self._window[GuiKeys.ScriptBox].Widget.see(
                selected_index[-1] if isinstance(selected_index, list) else selected_index)

    def update_existing_towers_and_script(self, activity_container: ActivityContainer,
                                          selected_script_index: Union[int, List[int]] = None):
        self.update_existing_towers(towers_container=activity_container.towers_container)
        self.update_script_box(activity_container=activity_container, selected_index=selected_script_index)
