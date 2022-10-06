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
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.towers_container import TowersContainer
from script_maker.statistics.money_statistics import calculate_cost


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata, controls_utils: GuiControlsUtils):
        self._window = window
        self._metadata = metadata
        self._controls_utils = controls_utils

    def update_difficulty(self):
        self.update_tower_types(towers_filter=lambda _: True)
        selected_hero_index = self._controls_utils.get_combo_selected_index(key=GuiKeys.HeroCombo)
        self._controls_utils.update_combo(key=GuiKeys.HeroCombo,
                                          values=GuiFormatters.format_hero_options(
                                              difficulty=self._metadata.difficulty),
                                          set_to_index=selected_hero_index)

    def update_selected_difficulty(self):
        selected_difficulty_index = list(DIFFICULTY_MAP.values()).index(self._metadata.difficulty)
        self._controls_utils.update_combo(key=GuiKeys.DifficultyListBox,
                                          set_to_index=selected_difficulty_index)

    def update_hero(self):
        self.update_tower_types(towers_filter=lambda _: True)

    def update_selected_hero(self):
        self._controls_utils.update_combo(key=GuiKeys.HeroCombo,
                                          set_to_index=list(HEROES_INFO.keys()).index(self._metadata.hero_type))

    def update_tower_types(self, towers_filter: Callable[[TowerInfo], bool]):
        tower_options = GuiFormatters.format_tower_options(difficulty=self._metadata.difficulty,
                                                           chosen_hero=self._metadata.hero_type,
                                                           towers_filter=towers_filter)

        self._controls_utils.update_listbox(key=GuiKeys.TowerTypesListBox, values=tower_options,
                                            set_to_index=self._controls_utils.get_list_box_selected_index(
                                                key=GuiKeys.TowerTypesListBox))
        self._controls_utils.add_alternating_colors(key=GuiKeys.TowerTypesListBox)

    def update_selected_tower_type(self, selected_tower_text: str):
        try:
            selected_tower_index = self._controls_utils.get_list_box_selected_index(key=GuiKeys.TowerTypesListBox)
        except ValueError:
            raise

        self._controls_utils.update_listbox(key=GuiKeys.TowerTypesListBox, set_to_index=selected_tower_index)
        self._controls_utils.update_input(key=GuiKeys.NewTowerTypeInput, value=selected_tower_text)

    def update_selected_existing_tower(self, is_hero: bool):
        if is_hero:
            self._controls_utils.disable_button(key=GuiKeys.TopUpgradeButton)
            self._controls_utils.disable_button(key=GuiKeys.MiddleUpgradeButton)
            self._controls_utils.disable_button(key=GuiKeys.BottomUpgradeButton)

    def update_total_cost(self, activity_container: ActivityContainer,
                          selected_script_index: Union[int, List[int]] = None):
        total_cost = calculate_cost(script_container=activity_container.script_container,
                                    towers_container=activity_container.towers_container,
                                    difficulty=self._metadata.difficulty)
        self._controls_utils.update_text(key=GuiKeys.TotalCostText, value=f"Total cost: {total_cost}")

        to_selection_cost = calculate_cost(script_container=activity_container.script_container,
                                           towers_container=activity_container.towers_container,
                                           difficulty=self._metadata.difficulty,
                                           end=selected_script_index)
        self._controls_utils.update_text(key=GuiKeys.CostToSelectionText,
                                         value=f"Cost to selection: {to_selection_cost}")

    def update_existing_towers(self, towers_container: TowersContainer):
        list_box_items = GuiFormatters.format_existing_towers(towers_container)
        self._controls_utils.update_listbox(
            key=GuiKeys.ExistingTowersListBox,
            values=list_box_items,
            set_to_index=self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ExistingTowersListBox))
        for i in range(len(list_box_items)):
            self._controls_utils.change_cell_color(key=GuiKeys.ExistingTowersListBox,
                                                   index=i,
                                                   color=towers_container.get_tower_color(tower_id=i))

    def update_script_box(self, activity_container: ActivityContainer, selected_index: Union[int, List[int]] = None):
        script_box_values: List[str] = []
        for action in activity_container.script_container:
            if isinstance(action, PauseEntry):
                script_box_values.append("Pause game.")
            if isinstance(action, WaitForMoneyEntry):
                script_box_values.append(f"Wait for {action.amount}$")
            if isinstance(action, CreateTowerEntry):
                script_box_values.append(f"Create: {action.name}({action.id}) | X: {action.x} Y: {action.y}")
            elif isinstance(action, UpgradeTowerEntry):
                script_box_values.append(f"Upgrade: ({action.id}) | tier: {action.tier}")
            elif isinstance(action, SellTowerEntry):
                script_box_values.append(f"Sell: ({action.id})")
            elif isinstance(action, ChangeTargetingEntry):
                script_box_values.append(f"Change targeting: ({action.id})")
            elif isinstance(action, ChangeSpecialTargetingEntry):
                script_box_values.append(f"Change special targeting: ({action.id})")

        self._controls_utils.update_listbox(key=GuiKeys.ScriptBox, values=script_box_values,
                                            set_to_index=selected_index)
        for i, script_entry in enumerate(activity_container.script_container):
            if isinstance(script_entry, ITowerModifyingScriptEntry):
                color = activity_container.towers_container.get_tower_color(tower_id=script_entry.id)
            else:
                color = GLOBAL_ENTRIES_COLOR

            self._controls_utils.change_cell_color(key=GuiKeys.ScriptBox, index=i, color=color)

        if selected_index is not None:
            self._window[GuiKeys.ScriptBox].Widget.see(
                selected_index[-1] if isinstance(selected_index, list) else selected_index)

    def update_existing_towers_and_script(self, activity_container: ActivityContainer,
                                          selected_script_index: Union[int, List[int]] = None):
        self.update_existing_towers(towers_container=activity_container.towers_container)
        self.update_script_box(activity_container=activity_container, selected_index=selected_script_index)
        self.update_total_cost(activity_container=activity_container, selected_script_index=selected_script_index)
