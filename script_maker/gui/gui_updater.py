from typing import Callable, Union

# noinspection PyPep8Naming
import PySimpleGUI as sg

from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import PauseEntry, WaitForMoneyEntry, \
    ITowerModifyingScriptEntry, CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, \
    ChangeSpecialTargetingEntry, CreateHeroEntry
from common.game_classes.script.script_parsing import dynamic_script_parsing
from common.game_classes.tower import Tower, Hero
from common.towers_info.game_info import g_heroes_info
from common.towers_info.info_classes import TowerInfo
from script_maker.gui.gui_colors import GLOBAL_ENTRIES_COLOR
from script_maker.gui.gui_controls_utils import GuiControlsUtils
from script_maker.gui.gui_formatters import GuiFormatters
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import DIFFICULTY_MAP
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.towers_container import TowersContainer
from script_maker.statistics.money_statistics import calculate_cost
from script_maker.utils.math_utils import get_last_if_list


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata, controls_utils: GuiControlsUtils):
        self._window = window
        self._metadata = metadata
        self._controls_utils = controls_utils

    def update_tower_and_hero_choices(self):
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
                                          set_to_index=list(g_heroes_info.keys()).index(self._metadata.hero_type))

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
                          selected_script_index: Union[int, list[int]] = None):
        total_cost = calculate_cost(script_container=activity_container.script_container,
                                    towers_container=activity_container.towers_container,
                                    metadata=self._metadata)
        self._controls_utils.update_text(key=GuiKeys.TotalCostText, value=f"Total cost: {total_cost}$")

        to_selection_cost = calculate_cost(script_container=activity_container.script_container,
                                           towers_container=activity_container.towers_container,
                                           metadata=self._metadata,
                                           end=get_last_if_list(selected_script_index))
        self._controls_utils.update_text(key=GuiKeys.CostToSelectionText,
                                         value=f"Cost to selection: {to_selection_cost}$")

    def update_existing_towers(self, towers_container: TowersContainer, selected_index: Union[int, list[int]] = None):
        list_box_items = GuiFormatters.format_existing_towers(towers_container)
        list_box_values: list[str] = list(list_box_items.values())
        selected_index = selected_index if selected_index is not None else \
            self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ExistingTowersListBox)

        self._controls_utils.update_listbox(
            key=GuiKeys.ExistingTowersListBox,
            values=list_box_values,
            set_to_index=selected_index)
        for i, list_box_item in enumerate(list_box_items.items()):
            tower_id, _ = list_box_item
            self._controls_utils.change_cell_color(key=GuiKeys.ExistingTowersListBox,
                                                   index=i,
                                                   color=towers_container.get_tower_color(tower_id=tower_id))

    def update_script_box(self, activity_container: ActivityContainer, selected_index: Union[int, list[int]] = None):
        script_box_values: list[str] = []
        for towers_container, action in dynamic_script_parsing(script_entries=activity_container.script_container):
            if isinstance(action, PauseEntry):
                script_box_values.append("Pause game.")
            elif isinstance(action, WaitForMoneyEntry):
                script_box_values.append(f"Wait for {action.amount}$")

            else:  # Tower specific
                if not isinstance(action, ITowerModifyingScriptEntry):
                    raise RuntimeError("Invalid action!")
                current_tower = towers_container[action.id]

                if isinstance(current_tower, Tower):
                    current_tower_name = current_tower.name
                elif isinstance(current_tower, Hero):
                    current_tower_name = "Hero"
                else:
                    raise RuntimeError("Invalid tower!")

                if isinstance(action, CreateTowerEntry):
                    script_box_values.append(f"Create: {action.name}({action.id}) | X: {action.x} Y: {action.y}")
                elif isinstance(action, CreateHeroEntry):
                    script_box_values.append(f"Create: Hero({action.id}) | X: {action.x} Y: {action.y}")
                elif isinstance(action, UpgradeTowerEntry):
                    if not isinstance(current_tower, Tower):
                        raise RuntimeError("Invalid action!")
                    formatted_tiers = GuiFormatters.format_tower_tiers(current_tower)
                    script_box_values.append(
                        f"Upgrade: {current_tower_name}({action.id}) | tier: {action.tier} | {formatted_tiers}")
                elif isinstance(action, SellTowerEntry):
                    script_box_values.append(f"Sell: {current_tower_name}({action.id})")
                elif isinstance(action, ChangeTargetingEntry):
                    script_box_values.append(f"Change targeting: {current_tower_name}({action.id})")
                elif isinstance(action, ChangeSpecialTargetingEntry):
                    script_box_values.append(f"Change special targeting: {current_tower_name}({action.id})")
                else:
                    raise RuntimeError("Invalid entry!")

        self._controls_utils.update_listbox(key=GuiKeys.ScriptBox, values=script_box_values,
                                            set_to_index=selected_index)
        for i, script_entry in enumerate(activity_container.script_container):
            if isinstance(script_entry, ITowerModifyingScriptEntry):
                color = activity_container.towers_container.get_tower_color(tower_id=script_entry.id)
            else:
                color = GLOBAL_ENTRIES_COLOR

            self._controls_utils.change_cell_color(key=GuiKeys.ScriptBox, index=i, color=color)

        if selected_index is not None:
            self._window[GuiKeys.ScriptBox].Widget.see(get_last_if_list(selected_index))

    def update_existing_towers_and_script(self, activity_container: ActivityContainer,
                                          selected_script_index: Union[int, list[int]] = None):
        self.update_existing_towers(towers_container=activity_container.towers_container)
        self.update_script_box(activity_container=activity_container, selected_index=selected_script_index)
        self.update_total_cost(activity_container=activity_container, selected_script_index=selected_script_index)
