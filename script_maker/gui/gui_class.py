import contextlib
import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Optional, Callable, Tuple

# noinspection PyPep8Naming
import PySimpleGUI as sg
from pydantic.json import pydantic_encoder

from common.game_classes.enums import UpgradeTier, TowerType
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_dataclasses import Script
from common.game_classes.script.script_entries_dataclasses import IScriptEntry, ITowerModifyingScriptEntry
from common.game_classes.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.monkey_knowledge.monkey_knowledge import g_monkey_knowledge
from common.towers_info.game_info import g_towers_info, g_heroes_info
from common.towers_info.info_classes import TowerInfo
from common.user_files import get_files_dir
from common.utils.upgrades_utils import is_tiers_text_valid
from script_maker.gui.gui_controls_utils import GuiControlsUtils
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_menu import GuiMenu
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_popups import popup_get_position, popup_get_file, popup_get_tower_type, popup_get_text, \
    popup_yes_no, popup_execute_method, popup_get_cost
from script_maker.gui.gui_types import ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater
from script_maker.hotkey_map import ScriptHotkeyMap
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.hotkeys.duplicate_tower_hotkeys import DuplicateTowerHotkeys
from script_maker.script.hotkeys.modify_tower_position_hotkeys import ModifyTowerPositionHotkeys
from script_maker.script.hotkeys.save_tower_hotkeys import SaveTowerHotkeys
from script_maker.script.hotkeys.tower_position_hotkeys import TowerPositionHotkeys
from script_maker.script.hotkeys.tower_types_hotkeys import TowerTypesHotkeys
from script_maker.utils.math_utils import increment_if_set


def update_existing_towers_and_script(method):
    @wraps(method)
    def _impl(self: "GuiClass", *method_args, **method_kwargs):
        try:
            return method(self, *method_args, **method_kwargs)
        finally:
            self._gui_updater.update_existing_towers_and_script(
                activity_container=self._activity_container,
                selected_script_index=self.get_next_index_in_script_box())

    return _impl


# noinspection PyUnusedLocal
class GuiClass:
    def __init__(self):
        self._window = sg.Window(title="BTD6 Scripter", layout=get_layout())
        self._selected_file_path: Optional[Path] = None
        self._activity_container = ActivityContainer()
        self._controls_utils = GuiControlsUtils(window=self._window)
        _, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo]))

        self._initialize_hotkey_classes()
        self._clip_boarded_script_entries: list[IScriptEntry] = []

        self._gui_updater = GuiUpdater(window=self._window, metadata=self._metadata,
                                       controls_utils=self._controls_utils)
        self.handle_view_all_towers(values=values)

    def _initialize_hotkey_classes(self):
        self._tower_position_hotkeys = TowerPositionHotkeys(
            observers=(lambda x, y: self._controls_utils.update_input(key=GuiKeys.XPositionInput, value=x),
                       lambda x, y: self._controls_utils.update_input(key=GuiKeys.YPositionInput, value=y)))
        self._tower_position_hotkeys.record_towers_position()

        self._save_tower_hotkeys = SaveTowerHotkeys(
            observers=(lambda: self._controls_utils.click_button(GuiKeys.SaveTowerButton),))
        self._save_tower_hotkeys.record_towers_saving()

        self._duplicate_tower_hotkeys = DuplicateTowerHotkeys(
            observers=(lambda: self._controls_utils.click_button(GuiKeys.DuplicateTowerButton),))
        self._duplicate_tower_hotkeys.record_towers_saving()

        self._modify_tower_position_hotkeys = ModifyTowerPositionHotkeys(
            observers=(lambda: self._controls_utils.click_button(GuiKeys.ModifyTowerPositionButton),))
        self._modify_tower_position_hotkeys.record_towers_saving()

        self._tower_types_hotkeys = self._initialize_tower_types_hotkeys()
        self._tower_types_hotkeys.record_towers_hotkeys()

    def _initialize_tower_types_hotkeys(self) -> TowerTypesHotkeys:
        def observer(tower_name: str):
            list_values = self._window[GuiKeys.TowerTypesListBox].get_list_values()

            tower_list_row = next(filter(lambda i: tower_name in i, list_values), None)

            self._gui_updater.update_selected_tower_type(selected_tower_text=tower_name)
            try:
                self._controls_utils.update_listbox(key=GuiKeys.TowerTypesListBox,
                                                    set_to_index=list_values.index(tower_list_row))
            except ValueError:
                pass

        return TowerTypesHotkeys(observers=(observer,))

    def _add_hotkey_binds(self):
        self._window.bind(ScriptHotkeyMap.new_script, GuiMenu.File.New)
        self._window.bind(ScriptHotkeyMap.import_script, GuiMenu.File.Import)
        self._window.bind(ScriptHotkeyMap.save_script, GuiMenu.File.Save)
        self._window.bind(ScriptHotkeyMap.save_script_as, GuiMenu.File.SaveAs)

        self._window.bind(ScriptHotkeyMap.view_all_towers, GuiMenu.ViewedTowers.All)
        self._window.bind(ScriptHotkeyMap.view_primary_towers, GuiMenu.ViewedTowers.Primary)
        self._window.bind(ScriptHotkeyMap.view_military_towers, GuiMenu.ViewedTowers.Military)
        self._window.bind(ScriptHotkeyMap.view_magic_towers, GuiMenu.ViewedTowers.Magic)
        self._window.bind(ScriptHotkeyMap.view_support_towers, GuiMenu.ViewedTowers.Support)

        self._window[GuiKeys.ScriptBox].bind(ScriptHotkeyMap.copy_towers_to_clipboard, GuiKeys.CopyToClipboard)
        self._window[GuiKeys.ScriptBox].bind(ScriptHotkeyMap.paste_towers_from_clipboard, GuiKeys.PasteClipboard)
        self._window[GuiKeys.ScriptBox].bind(ScriptHotkeyMap.double_click, GuiKeys.DoubleClick)

        self._window.bind(ScriptHotkeyMap.save_upgraded, GuiKeys.SaveUpgradedButton)
        self._window.bind(ScriptHotkeyMap.keyboard_mouse, GuiKeys.KeyboardMouseButton)
        self._window.bind(ScriptHotkeyMap.upgrade_top, GuiKeys.TopUpgradeButton)
        self._window.bind(ScriptHotkeyMap.upgrade_middle, GuiKeys.MiddleUpgradeButton)
        self._window.bind(ScriptHotkeyMap.upgrade_bottom, GuiKeys.BottomUpgradeButton)
        self._window.bind(ScriptHotkeyMap.sell, GuiKeys.SellButton)
        self._window.bind(ScriptHotkeyMap.change_targeting, GuiKeys.TargetingButton)
        self._window.bind(ScriptHotkeyMap.change_special_targeting, GuiKeys.SpecialTargetingButton)
        self._window.bind(ScriptHotkeyMap.delete_tower, GuiKeys.DeleteTowerButton)
        self._window.bind(ScriptHotkeyMap.modify_tower_type, GuiKeys.ModifyTowerTypeButton)
        self._window.bind(ScriptHotkeyMap.pause_game, GuiKeys.PauseGameButton)
        self._window.bind(ScriptHotkeyMap.delete_script, GuiKeys.DeleteFromScriptButton)
        self._window.bind(ScriptHotkeyMap.delete_up_script, GuiKeys.MoveUpInScriptButton)
        self._window.bind(ScriptHotkeyMap.move_down_script, GuiKeys.MoveDownInScriptButton)

    def run(self):
        callback_map = self.get_callback_map()
        self._add_hotkey_binds()
        while True:
            event, values = self._window.read()

            if event in callback_map:
                callback_map[event](values)

            if event == sg.WIN_CLOSED:
                break

        self._window.close()

    def get_next_index_in_script_box(self) -> int:
        last_selected_index = self._controls_utils.get_list_box_last_selected_index(key=GuiKeys.ScriptBox)
        return increment_if_set(value=last_selected_index)

    @contextlib.contextmanager
    def _retrieve_next_script_box_index_and_update_activity(self) -> int:
        entry_index_to_select = self.get_next_index_in_script_box()
        try:
            yield entry_index_to_select
        finally:
            self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                                selected_script_index=entry_index_to_select)

    @contextlib.contextmanager
    def _retrieve_next_script_box_index_and_update_script(self):
        entry_index_to_select = self.get_next_index_in_script_box()
        try:
            yield entry_index_to_select
        finally:
            self._gui_updater.update_script_box(activity_container=self._activity_container,
                                                selected_index=entry_index_to_select)

    def _get_popups_position(self) -> Tuple[int, int]:
        window_location = self._window.current_location()
        return (int(window_location[0] + (self._window.size[0] / 2)),
                int(window_location[1] + (self._window.size[1] / 2)))

    def _get_selected_towers_id(self) -> list[int]:
        selected_towers_indexes = self._controls_utils.get_list_box_selected_indexes(
            key=GuiKeys.ExistingTowersListBox)
        return [list(self._activity_container.towers_container.keys())[i] for i in selected_towers_indexes]

    def handle_change_difficulty(self, values: ValuesType):
        self._metadata.difficulty = DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]]
        self._gui_updater.update_tower_and_hero_choices()

    def handle_change_hero(self, values: ValuesType):
        self._metadata.hero_type = GuiParsers.parse_selected_hero(hero_str=values[GuiKeys.HeroCombo])
        self._gui_updater.update_hero()

    def handle_select_tower_type(self, values: ValuesType):
        try:
            tower_name = GuiParsers.parse_selected_tower(
                tower_str=self._controls_utils.get_selected_value_for_list_box(values=values,
                                                                               key=GuiKeys.TowerTypesListBox))
            self._gui_updater.update_selected_tower_type(selected_tower_text=tower_name)
        except ValueError:
            self._controls_utils.unselect_listbox(key=GuiKeys.TowerTypesListBox)
            sg.popup("You must select exactly 1 tower type")

    def handle_select_script_box(self, values: ValuesType):
        self._gui_updater.update_total_cost(
            activity_container=self._activity_container,
            selected_script_index=self._controls_utils.get_list_box_last_selected_index(key=GuiKeys.ScriptBox))

    def handle_select_existing_tower(self, values: ValuesType):
        try:
            selected_tower_value = GuiParsers.parse_existing_tower(
                tower_str=self._controls_utils.get_selected_value_for_list_box(values=values,
                                                                               key=GuiKeys.ExistingTowersListBox))
            self._gui_updater.update_selected_existing_tower(
                is_hero=GuiParsers.is_selected_tower_hero(tower_str=selected_tower_value))
        except ValueError:
            pass

    @staticmethod
    def handle_keyboard_mouse(values: ValuesType):
        os.system("start ms-settings:easeofaccess-mouse")

    def _handle_save_tower(self, values: ValuesType) -> int:
        if not self._controls_utils.are_values_set(values, GuiKeys.NewTowerTypeInput, GuiKeys.XPositionInput,
                                                   GuiKeys.YPositionInput):
            sg.popup("You didn't fill all of the data!")
            raise ValueError

        tower_name = values[GuiKeys.NewTowerTypeInput]
        tower_x = int(values[GuiKeys.XPositionInput])
        tower_y = int(values[GuiKeys.YPositionInput])
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            if "Hero" == values[GuiKeys.NewTowerTypeInput]:
                if not self._activity_container.is_hero_placeable():
                    sg.popup("Your Hero is already placed!")
                    raise ValueError

                return self._activity_container.add_hero(x=tower_x,
                                                         y=tower_y,
                                                         index=entry_index_to_select)

            else:
                return self._activity_container.add_new_tower(name=tower_name,
                                                              x=tower_x,
                                                              y=tower_y,
                                                              index=entry_index_to_select)

    def handle_save_tower(self, values: ValuesType):
        try:
            self._handle_save_tower(values=values)
        except ValueError:
            pass

    def handle_save_upgraded(self, values: ValuesType):
        try:
            text = popup_get_text(message="Enter tower upgrade(e.g: 102): ",
                                  validator=is_tiers_text_valid,
                                  error_message="Invalid tower upgrades entered!",
                                  location=self._get_popups_position())
            selected_tower_id = self._handle_save_tower(values=values)
        except ValueError:
            return

        tier_map = {
            tier: level for tier, level in zip((UpgradeTier.top, UpgradeTier.middle, UpgradeTier.bottom),
                                               (int(i) for i in text))
        }
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for tier, level in tier_map.items():
                if not level:
                    continue

                for _ in range(level):
                    self._activity_container.upgrade_tower(tower_id=selected_tower_id, tier=tier,
                                                           index=entry_index_to_select)
                    entry_index_to_select = increment_if_set(value=entry_index_to_select)

    def _is_tower_modifiable(self, tower_id: int) -> bool:
        return not self._activity_container.towers_container[tower_id].sold

    def _handle_tower_upgrade(self, tier: UpgradeTier):

        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
                if not self._is_tower_modifiable(tower_id=selected_tower_id):
                    # TODO: enable upgrading the lines before selling.
                    sg.popup("Tower can't be modified!")
                    continue

                try:
                    self._activity_container.upgrade_tower(tower_id=selected_tower_id, tier=tier,
                                                           index=entry_index_to_select)
                except ValueError:
                    sg.popup("Invalid upgrade for tower!")

    def handle_top_upgrade(self, values: ValuesType):
        self._handle_tower_upgrade(tier=UpgradeTier.top)

    def handle_middle_upgrade(self, values: ValuesType):
        self._handle_tower_upgrade(tier=UpgradeTier.middle)

    def handle_bottom_upgrade(self, values: ValuesType):
        self._handle_tower_upgrade(tier=UpgradeTier.bottom)

    def handle_sell_tower(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
                try:
                    self._activity_container.sell_tower(tower_id=selected_tower_id, index=entry_index_to_select)
                except ValueError:
                    sg.popup("The tower is already sold!")

    def handle_change_targeting(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
                if not self._is_tower_modifiable(tower_id=selected_tower_id):
                    # TODO: enable upgrading the lines before selling.
                    sg.popup("Tower can't be modified!")
                    continue

                self._activity_container.change_targeting(tower_id=selected_tower_id, index=entry_index_to_select)

    def handle_change_special_targeting(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
                if not self._is_tower_modifiable(tower_id=selected_tower_id):
                    # TODO: enable upgrading the lines before selling.
                    sg.popup("Tower can't be modified!")
                    continue

                self._activity_container.change_special_targeting(tower_id=selected_tower_id,
                                                                  index=entry_index_to_select)

    @update_existing_towers_and_script
    def handle_modify_tower_position(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            with self._tower_position_hotkeys.pause_capture():
                try:
                    x, y = popup_get_position(title=f"Modify position for tower: {selected_tower_id}",
                                              location=self._get_popups_position())
                    self._activity_container.change_position(tower_id=selected_tower_id, x=x, y=y)
                except ValueError:
                    pass

    @update_existing_towers_and_script
    def handle_modify_tower_type(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            try:
                tower_type = popup_get_tower_type(title=f"Select type for tower: {selected_tower_id}",
                                                  location=self._get_popups_position())
            except ValueError:
                continue

            self._activity_container.change_tower_type(tower_id=selected_tower_id, tower_type=tower_type)

    @update_existing_towers_and_script
    def handle_duplicate_tower(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            with self._tower_position_hotkeys.pause_capture():
                try:
                    x, y = popup_get_position(title=f"Set position for duplicated tower: {selected_tower_id}",
                                              location=self._get_popups_position())
                    self._activity_container.duplicate_tower(tower_id=selected_tower_id, new_tower_x=x, new_tower_y=y)
                except ValueError:
                    pass

    @update_existing_towers_and_script
    def handle_delete_tower(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            self._activity_container.delete_tower(tower_id=selected_tower_id)

    def handle_delete_from_script(self, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to remove!")
            return

        selected_indexes = self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ScriptBox)
        for selected_entry_index in selected_indexes[::-1]:
            # Going in reverse to allow deletion of towers.
            try:
                self._activity_container.delete_entry(selected_entry_index)
            except ValueError:
                sg.popup("Invalid deletion attempted.")
                continue

        index_to_select = selected_indexes[0] if len(selected_indexes) == 1 else None
        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=index_to_select)

    def handle_move_up_on_script(self, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_indexes = self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ScriptBox)

        for selected_entry_index in selected_indexes:
            # Order of iteration is important to ensure all items can move up.
            try:
                self._activity_container.move_script_entry_up(entry_index=selected_entry_index)
            except ValueError:
                sg.popup("Item already first!")
                return

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=[i - 1 for i in selected_indexes])

    def handle_move_down_on_script(self, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_indexes = self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ScriptBox)
        for selected_entry_index in selected_indexes[::-1]:
            # Going in reverse to ensure that the last entry is valid to move
            try:
                self._activity_container.move_script_entry_down(entry_index=selected_entry_index)
            except ValueError:
                sg.popup("Item already last!")
                return

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=[i + 1 for i in selected_indexes])

    @update_existing_towers_and_script
    def handle_new_button(self, values: ValuesType):
        self._activity_container.reset_activity()

    def _handle_save(self, selected_file_path: Path = None):
        try:
            self._selected_file_path = selected_file_path or popup_get_file(
                message="Please select save path",
                default_path=get_files_dir(),
                save_as=True,
                file_types=(("Json files", "json"),),
                location=self._get_popups_position())
        except ValueError:
            return

        with self._selected_file_path.open("w") as of:
            json.dump(Script(metadata=self._metadata, script=self._activity_container.script_container.data), of,
                      default=pydantic_encoder)

    def handle_save_as_button(self, values: ValuesType):
        self._handle_save()

    def handle_save_button(self, values: ValuesType):
        self._handle_save(selected_file_path=self._selected_file_path)

    def _import_selected_script(self):
        with self._selected_file_path.open("r") as of:
            json_dict = json.load(of)

        loaded_metadata = parse_metadata(json_dict=json_dict)
        self._metadata.difficulty = loaded_metadata.difficulty
        self._metadata.hero_type = loaded_metadata.hero_type
        self._gui_updater.update_selected_difficulty()
        self._gui_updater.update_selected_hero()
        self._gui_updater.update_hero()
        self._gui_updater.update_tower_and_hero_choices()

        self._activity_container.script_container = import_script(script_dict=json_dict["script"])
        self._activity_container.towers_container = parse_towers_from_script(
            script_entries=self._activity_container.script_container)

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container)

    def import_script(self, script_path: Path):
        self._selected_file_path = script_path
        self._import_selected_script()

    def handle_import_button(self, values: ValuesType):
        try:
            selected_file_path = popup_get_file(message="Please select file to import",
                                                default_path=get_files_dir(),
                                                file_types=(("Json files", "json"),),
                                                location=self._get_popups_position())
            self.import_script(script_path=selected_file_path)
        except ValueError:
            pass

    def _handle_view_towers(self, values: ValuesType, towers_filter: Callable[[TowerInfo], bool]):
        self._gui_updater.update_tower_types(towers_filter=towers_filter)

    def handle_view_all_towers(self, values: ValuesType):
        self._handle_view_towers(values=values, towers_filter=lambda _: True)

    def handle_view_primary_towers(self, values: ValuesType):
        self._handle_view_towers(values=values, towers_filter=lambda x: x.type == TowerType.Primary)

    def handle_view_military_towers(self, values: ValuesType):
        self._handle_view_towers(values=values, towers_filter=lambda x: x.type == TowerType.Military)

    def handle_view_magic_towers(self, values: ValuesType):
        self._handle_view_towers(values=values, towers_filter=lambda x: x.type == TowerType.Magic)

    def handle_view_support_towers(self, values: ValuesType):
        self._handle_view_towers(values=values, towers_filter=lambda x: x.type == TowerType.Support)

    def handle_copy_on_script(self, values: ValuesType):
        self._clip_boarded_script_entries = [self._activity_container.script_container[i] for i in
                                             self._controls_utils.get_list_box_selected_indexes(
                                                 key=GuiKeys.ScriptBox)]

    def handle_paste_on_script(self, values: ValuesType):
        if not self._clip_boarded_script_entries:
            return

        self._activity_container.duplicate_script_entries(entries=self._clip_boarded_script_entries,
                                                          new_index=self.get_next_index_in_script_box())
        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container)

    def handle_double_click_on_script(self, values: ValuesType):
        selected_indexes = self._controls_utils.get_list_box_selected_indexes(key=GuiKeys.ScriptBox)
        if len(selected_indexes) != 1:
            return

        action = self._activity_container.script_container[selected_indexes[0]]
        if isinstance(action, ITowerModifyingScriptEntry):
            tower_index = list(self._activity_container.towers_container.keys()).index(action.id)
            self._gui_updater.update_existing_towers(towers_container=self._activity_container.towers_container,
                                                     selected_index=tower_index)

    def handle_pause_button(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_script() as selected_index:
            self._activity_container.add_pause_entry(index=selected_index)

    def handle_wait_for_money_button(self, values: ValuesType):
        try:
            amount_of_money = GuiParsers.parse_amount_of_money(values[GuiKeys.WaitForMoneyInput])
        except ValueError:
            sg.popup("Invalid amount of money to wait for")
            return

        with self._retrieve_next_script_box_index_and_update_script() as selected_index:
            self._activity_container.add_wait_for_money_entry(amount=amount_of_money, index=selected_index)

    def handle_remove_obstacle_button(self, values: ValuesType):

        with self._tower_position_hotkeys.pause_capture():
            try:
                x, y = popup_get_position(title=f"Select obstacle position",
                                          location=self._get_popups_position())
                cost = popup_get_cost(message="Enter cost for the obstacle removal",
                                      location=self._get_popups_position())
                with self._retrieve_next_script_box_index_and_update_script() as selected_index:
                    self._activity_container.add_remove_obstacle_entry(x=x, y=y, cost=cost, index=selected_index)
            except ValueError:
                sg.popup("Error. please try again")

    def handle_scan_towers_info(self, values: ValuesType):
        if not popup_yes_no(
                "Towers scan: Scanning towers information for prices from wiki.\n"
                "NOTE: this might take a few minutes\n"
                "Press yes to start scan",
                title="Towers update",
                location=self._get_popups_position()):
            return

        def _scan():
            print("Scanning towers info")
            g_towers_info.update_info()

        popup_execute_method("Scanning towers.\nYou can use your computer normally.", title="Scanning towers",
                             method=_scan, done_text="Done scanning.",
                             location=self._get_popups_position())
        self._gui_updater.update_tower_and_hero_choices()

    def handle_scan_heroes_info(self, values: ValuesType):
        if not popup_yes_no(
                "Heroes scan: Scanning heroes information for prices from wiki.\n"
                "NOTE: this might take a few minutes\n"
                "Press yes to start scan",
                title="Heroes update",
                location=self._get_popups_position()):
            return

        def _scan():
            print("Scanning heroes info")
            g_heroes_info.update_info()

        popup_execute_method("Scanning heroes.\nYou can use your computer normally.", title="Scanning heroes",
                             method=_scan, done_text="Done scanning.",
                             location=self._get_popups_position())
        self._gui_updater.update_tower_and_hero_choices()

    def handle_scan_monkey_knowledge_info(self, values: ValuesType):
        # TODO: Enable touching after the screenshots are taken
        # TODO: center the popups
        if not popup_yes_no(
                "Knowledge scan: In order to perform a knowledge scan you need to open BTD6 on the main screen.\n"
                "Please do not touch your computer until the scan is completed\n"
                "Right after clicking yes please click on BTD6 to keep it on focus and on top\n"
                "You could start to use the computer after you see the primary tab for the 2nd time\n"
                "NOTE: this might take a few minutes\n"
                "Press yes to start scan",
                title="Monkey knowledge update",
                line_width=1000,
                location=self._get_popups_position()):
            return

        def _scan():
            print("Scanning knowledge")
            time.sleep(3)
            g_monkey_knowledge.update_info()

        popup_execute_method("Please don't touch your computer until finished", title="Scanning knowledge",
                             method=_scan, done_text="Done scanning, you can use your computer",
                             location=self._get_popups_position())

    def get_callback_map(self) -> dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty,
            GuiKeys.HeroCombo: self.handle_change_hero,
            GuiKeys.TowerTypesListBox: self.handle_select_tower_type,
            GuiKeys.ScriptBox: self.handle_select_script_box,
            GuiKeys.ExistingTowersListBox: self.handle_select_existing_tower,
            GuiKeys.KeyboardMouseButton: self.handle_keyboard_mouse,
            GuiKeys.SaveTowerButton: self.handle_save_tower,
            GuiKeys.SaveUpgradedButton: self.handle_save_upgraded,
            GuiKeys.TopUpgradeButton: self.handle_top_upgrade,
            GuiKeys.MiddleUpgradeButton: self.handle_middle_upgrade,
            GuiKeys.BottomUpgradeButton: self.handle_bottom_upgrade,
            GuiKeys.SellButton: self.handle_sell_tower,
            GuiKeys.TargetingButton: self.handle_change_targeting,
            GuiKeys.SpecialTargetingButton: self.handle_change_special_targeting,
            GuiKeys.ModifyTowerPositionButton: self.handle_modify_tower_position,
            GuiKeys.ModifyTowerTypeButton: self.handle_modify_tower_type,
            GuiKeys.DuplicateTowerButton: self.handle_duplicate_tower,
            GuiKeys.DeleteTowerButton: self.handle_delete_tower,
            GuiKeys.DeleteFromScriptButton: self.handle_delete_from_script,
            GuiKeys.MoveUpInScriptButton: self.handle_move_up_on_script,
            GuiKeys.MoveDownInScriptButton: self.handle_move_down_on_script,
            GuiMenu.File.Save: self.handle_save_button,
            GuiMenu.File.SaveAs: self.handle_save_as_button,
            GuiMenu.File.New: self.handle_new_button,
            GuiMenu.File.Import: self.handle_import_button,
            GuiMenu.ViewedTowers.All: self.handle_view_all_towers,
            GuiMenu.ViewedTowers.Primary: self.handle_view_primary_towers,
            GuiMenu.ViewedTowers.Military: self.handle_view_military_towers,
            GuiMenu.ViewedTowers.Magic: self.handle_view_magic_towers,
            GuiMenu.ViewedTowers.Support: self.handle_view_support_towers,
            GuiMenu.Scan.TowersInfo: self.handle_scan_towers_info,
            GuiMenu.Scan.HeroesInfo: self.handle_scan_heroes_info,
            GuiMenu.Scan.MonkeyKnowledge: self.handle_scan_monkey_knowledge_info,
            GuiKeys.ScriptBox + GuiKeys.CopyToClipboard: self.handle_copy_on_script,
            GuiKeys.ScriptBox + GuiKeys.PasteClipboard: self.handle_paste_on_script,
            GuiKeys.ScriptBox + GuiKeys.DoubleClick: self.handle_double_click_on_script,
            GuiKeys.PauseGameButton: self.handle_pause_button,
            GuiKeys.WaitForMoneyButton: self.handle_wait_for_money_button,
            GuiKeys.RemoveObstacleButton: self.handle_remove_obstacle_button
        }
