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
        self.update_tower_types(towers_filter=lambda _: True)
        selected_hero_index = self._controls_utils.get_combo_selected_index(key=GuiKeys.HeroCombo)
        self._controls_utils.update_combo(combo=self._window[GuiKeys.HeroCombo],
                                          values=get_hero_options(difficulty=self._metadata.difficulty),
                                          set_to_index=selected_hero_index)

    def update_selected_difficulty(self):
        selected_difficulty_index = list(DIFFICULTY_MAP.values()).index(self._metadata.difficulty)
        self._controls_utils.update_combo(combo=self._window[GuiKeys.DifficultyListBox],
                                          set_to_index=selected_difficulty_index)

    def update_hero(self):
        self.update_tower_types(towers_filter=lambda _: True)

    def update_selected_hero(self):
        self._controls_utils.update_combo(combo=self._window[GuiKeys.HeroCombo],
                                          set_to_index=list(HEROES_INFO.keys()).index(self._metadata.hero_type))

    def update_tower_types(self, towers_filter: Callable[[TowerInfo], bool]):
        tower_options = get_tower_options(difficulty=self._metadata.difficulty,
                                          chosen_hero=self._metadata.hero_type,
                                          towers_filter=towers_filter)

        list_box = self._window[GuiKeys.TowerTypesListBox]
        self._controls_utils.update_listbox(listbox=list_box, values=tower_options,
                                            set_to_index=self._controls_utils.get_list_box_selected_index(
                                                key=GuiKeys.TowerTypesListBox))
        self._controls_utils.add_alternating_colors(listbox_widget=list_box.widget)

    def update_selected_tower_type(self, selected_tower_text: str):
        try:
            selected_tower_index = self._controls_utils.get_list_box_selected_index(key=GuiKeys.TowerTypesListBox)
        except ValueError:
            raise

        self._controls_utils.update_listbox(listbox=self._window[GuiKeys.TowerTypesListBox],
                                            set_to_index=selected_tower_index)
        self._controls_utils.update_input(input_element=self._window[GuiKeys.NewTowerTypeInput],
                                          value=selected_tower_text)

    def update_selected_existing_tower(self, is_hero: bool):
        if is_hero:
            self._controls_utils.disable_button(self._window[GuiKeys.TopUpgradeButton])
            self._controls_utils.disable_button(self._window[GuiKeys.MiddleUpgradeButton])
            self._controls_utils.disable_button(self._window[GuiKeys.BottomUpgradeButton])

    def update_existing_towers(self, towers_container: TowersContainer):
        listbox = self._window[GuiKeys.ExistingTowersListBox]
        list_box_items = GuiFormatters.format_existing_towers(towers_container)
        self._controls_utils.update_listbox(
            listbox=listbox,
            values=list_box_items,
            set_to_index=self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ExistingTowersListBox))
        for i in range(len(list_box_items)):
            self._controls_utils.change_cell_color(listbox_widget=listbox.widget, index=i,
                                                   color=towers_container.get_tower_color(tower_id=i))

    def update_script_box(self, activity_container: ActivityContainer, selected_index: Union[int, List[int]] = None):
        output: List[str] = []
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

        listbox = self._window[GuiKeys.ScriptBox]
        self._controls_utils.update_listbox(listbox=listbox, set_to_index=selected_index)
        for i, script_entry in enumerate(activity_container.script_container):
            if isinstance(script_entry, ITowerModifyingScriptEntry):
                self._controls_utils.change_cell_color(listbox_widget=listbox.widget, index=i,
                                                       color=activity_container.towers_container.get_tower_color(
                                                           tower_id=script_entry.id))
            else:
                self._controls_utils.change_cell_color(listbox_widget=listbox.widget, index=i,
                                                       color=GLOBAL_ENTRIES_COLOR)

        if selected_index is not None:
            self._window[GuiKeys.ScriptBox].Widget.see(
                selected_index[-1] if isinstance(selected_index, list) else selected_index)

    def update_existing_towers_and_script(self, activity_container: ActivityContainer,
                                          selected_script_index: Union[int, List[int]] = None):
        self.update_existing_towers(towers_container=activity_container.towers_container)
        self.update_script_box(activity_container=activity_container, selected_index=selected_script_index)
