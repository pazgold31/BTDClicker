import contextlib
import json
import os
from functools import wraps
from typing import Dict, Optional, List, Callable

# noinspection PyPep8Naming
import PySimpleGUI as sg
from pydantic.json import pydantic_encoder

from common.game_classes.enums import UpgradeTier, TowerType
from common.game_classes.script.script_dataclasses import GameMetadata, Script, IScriptEntry
from common.game_classes.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.towers_info.info_classes import TowerInfo
from common.user_files import get_files_dir
from script_maker.gui.gui_controls_utils import GuiControlsUtils
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_menu import GuiMenu
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_popups import popup_get_position, popup_get_file
from script_maker.gui.gui_types import ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.hotkeys.tower_position_hotkeys import TowerPositionHotkeys


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
        self._selected_file_path: Optional[str] = None
        self._activity_container = ActivityContainer()
        self._controls_utils = GuiControlsUtils(window=self._window)
        _, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo]))

        self._script_global_hotkeys = TowerPositionHotkeys(x_pos=self._window[GuiKeys.XPositionInput],
                                                           y_pos=self._window[GuiKeys.YPositionInput],
                                                           tower_types=self._window[GuiKeys.TowerTypesListBox])
        self._script_global_hotkeys.record_towers_position()
        self._script_global_hotkeys.record_towers_hotkeys()
        self._clip_boarded_script_entries: List[IScriptEntry] = []

        self._gui_updater = GuiUpdater(window=self._window, metadata=self._metadata,
                                       controls_utils=self._controls_utils)
        self.handle_view_all_towers(values=values)

    def _add_hotkey_binds(self):
        self._window.bind("<Control-o>", GuiMenu.File.Import)
        self._window.bind("<Control-s>", GuiMenu.File.Save)
        self._window.bind("<Control-Shift-S>", GuiMenu.File.SaveAs)

        self._window.bind("<Control_L>1", GuiMenu.ViewedTowers.All)
        self._window.bind("<Control_L>2", GuiMenu.ViewedTowers.Primary)
        self._window.bind("<Control_L>3", GuiMenu.ViewedTowers.Military)
        self._window.bind("<Control_L>4", GuiMenu.ViewedTowers.Magic)
        self._window.bind("<Control_L>5", GuiMenu.ViewedTowers.Support)

        self._window[GuiKeys.ScriptBox].bind("<Control_L>c", GuiKeys.CopyToClipboard)
        self._window[GuiKeys.ScriptBox].bind("<Control_L>v", GuiKeys.PasteClipboard)

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

    def get_next_index_in_script_box(self):
        last_selected_index = self._controls_utils.get_list_box_last_selected_index(key=GuiKeys.ScriptBox)
        return None if last_selected_index is None else last_selected_index + 1

    @contextlib.contextmanager
    def _retrieve_next_script_box_index_and_update_activity(self):
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

    def _get_selected_towers_id(self) -> List[int]:
        selected_towers_indexes = self._controls_utils.get_list_box_selected_indexes(
            key=GuiKeys.ExistingTowersListBox)
        return [list(self._activity_container.towers_container.keys())[i] for i in selected_towers_indexes]

    def handle_change_difficulty(self, values: ValuesType):
        self._metadata.difficulty = DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]]
        self._gui_updater.update_difficulty()

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

    def handle_save_tower(self, values: ValuesType):
        if not self._controls_utils.are_values_set(values, GuiKeys.NewTowerTypeInput, GuiKeys.XPositionInput,
                                                   GuiKeys.YPositionInput):
            sg.popup("You didn't fill all of the data!")
            return

        tower_name = values[GuiKeys.NewTowerTypeInput]
        tower_x = int(values[GuiKeys.XPositionInput])
        tower_y = int(values[GuiKeys.YPositionInput])
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            if "Hero" == values[GuiKeys.NewTowerTypeInput]:
                if not self._activity_container.is_hero_placeable():
                    sg.popup("Your Hero is already placed!")
                    return

                self._activity_container.add_hero(name=tower_name,
                                                  x=tower_x,
                                                  y=tower_y,
                                                  index=entry_index_to_select)

            else:
                self._activity_container.add_new_tower(name=tower_name,
                                                       x=tower_x,
                                                       y=tower_y,
                                                       index=entry_index_to_select)

    def _handle_tower_upgrade(self, tier: UpgradeTier):

        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
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
                self._activity_container.change_targeting(tower_id=selected_tower_id, index=entry_index_to_select)

    def handle_change_special_targeting(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_activity() as entry_index_to_select:
            for selected_tower_id in self._get_selected_towers_id():
                self._activity_container.change_special_targeting(tower_id=selected_tower_id,
                                                                  index=entry_index_to_select)

    @update_existing_towers_and_script
    def handle_modify_tower(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            with self._script_global_hotkeys.pause_capture():
                x, y = popup_get_position(title=f"Modify position for tower: {selected_tower_id}")
                self._activity_container.change_position(tower_id=selected_tower_id, x=x, y=y)

    @update_existing_towers_and_script
    def handle_duplicate_tower(self, values: ValuesType):
        for selected_tower_id in self._get_selected_towers_id():
            with self._script_global_hotkeys.pause_capture():
                x, y = popup_get_position(title=f"Set position for duplicated tower: {selected_tower_id}")
                self._activity_container.duplicate_tower(tower_id=selected_tower_id, new_tower_x=x, new_tower_y=y)

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

    def handle_save_button(self, values: ValuesType):

        self._selected_file_path = self._selected_file_path or popup_get_file(message="Please select file to import",
                                                                              default_path=get_files_dir(),
                                                                              file_types=(("Json files", "json"),))

        with self._selected_file_path.open("w") as of:
            json.dump(Script(metadata=self._metadata, script=self._activity_container.script_container), of,
                      default=pydantic_encoder)

    def handle_import_button(self, values: ValuesType):

        self._selected_file_path = popup_get_file(message="Please select file to import",
                                                  default_path=get_files_dir(),
                                                  file_types=(("Json files", "json"),))

        with self._selected_file_path.open("r") as of:
            json_dict = json.load(of)

        loaded_metadata = parse_metadata(json_dict=json_dict)
        self._metadata.difficulty = loaded_metadata.difficulty
        self._metadata.hero_type = loaded_metadata.hero_type
        self._gui_updater.update_selected_difficulty()
        self._gui_updater.update_selected_hero()
        self._gui_updater.update_hero()
        self._gui_updater.update_difficulty()

        self._activity_container.script_container = import_script(script_dict=json_dict["script"])
        self._activity_container.towers_container = parse_towers_from_script(
            script_entries=self._activity_container.script_container,
            metadata=self._metadata)

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container)

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

    def handle_pause_button(self, values: ValuesType):
        with self._retrieve_next_script_box_index_and_update_script() as selected_index:
            self._activity_container.add_pause_entry(index=selected_index)

    def handle_wait_for_money(self, values: ValuesType):
        try:
            amount_of_money = GuiParsers.parse_amount_of_money(values[GuiKeys.WaitForMoneyInput])
        except ValueError:
            sg.popup("Invalid amount of money to wait for")
            return

        with self._retrieve_next_script_box_index_and_update_script() as selected_index:
            self._activity_container.add_wait_for_money_entry(amount=amount_of_money, index=selected_index)

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty,
            GuiKeys.HeroCombo: self.handle_change_hero,
            GuiKeys.TowerTypesListBox: self.handle_select_tower_type,
            GuiKeys.ExistingTowersListBox: self.handle_select_existing_tower,
            GuiKeys.KeyboardMouseButton: self.handle_keyboard_mouse,
            GuiKeys.SaveTowerButton: self.handle_save_tower,
            GuiKeys.TopUpgradeButton: self.handle_top_upgrade,
            GuiKeys.MiddleUpgradeButton: self.handle_middle_upgrade,
            GuiKeys.BottomUpgradeButton: self.handle_bottom_upgrade,
            GuiKeys.SellButton: self.handle_sell_tower,
            GuiKeys.TargetingButton: self.handle_change_targeting,
            GuiKeys.SpecialTargetingButton: self.handle_change_special_targeting,
            GuiKeys.ModifyTowerButton: self.handle_modify_tower,
            GuiKeys.DuplicateTowerButton: self.handle_duplicate_tower,
            GuiKeys.DeleteTowerButton: self.handle_delete_tower,
            GuiKeys.DeleteFromScriptButton: self.handle_delete_from_script,
            GuiKeys.MoveUpInScriptButton: self.handle_move_up_on_script,
            GuiKeys.MoveDownInScriptButton: self.handle_move_down_on_script,
            GuiMenu.File.Save: self.handle_save_button,
            GuiMenu.File.Import: self.handle_import_button,
            GuiMenu.ViewedTowers.All: self.handle_view_all_towers,
            GuiMenu.ViewedTowers.Primary: self.handle_view_primary_towers,
            GuiMenu.ViewedTowers.Military: self.handle_view_military_towers,
            GuiMenu.ViewedTowers.Magic: self.handle_view_magic_towers,
            GuiMenu.ViewedTowers.Support: self.handle_view_support_towers,
            GuiKeys.ScriptBox + GuiKeys.CopyToClipboard: self.handle_copy_on_script,
            GuiKeys.ScriptBox + GuiKeys.PasteClipboard: self.handle_paste_on_script,
            GuiKeys.PauseGameButton: self.handle_pause_button,
            GuiKeys.WaitForMoneyButton: self.handle_wait_for_money
        }
