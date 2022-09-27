import json
import os
from typing import Dict

# noinspection PyPep8Naming
import PySimpleGUI as sg
from pydantic.json import pydantic_encoder

from common.game_classes.enums import UpgradeTier, TowerType
from common.game_classes.script.script_dataclasses import GameMetadata, Script
from common.game_classes.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.user_files import get_files_dir
from script_maker.gui.gui_controls_utils import are_values_set, get_selected_indexes_for_list_box, \
    get_last_selected_index_for_list_box
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_menu import GuiMenu
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_popups import popup_get_position
from script_maker.gui.gui_types import EventType, ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater
from script_maker.script.activity_container import ActivityContainer
from script_maker.script.script_hotkeys import ScriptHotkeys


class GuiClass:
    def __init__(self, ):
        self._window = sg.Window(title="BTD6 Scripter", layout=get_layout())
        self._script_global_hotkeys = ScriptHotkeys(x_pos=self._window[GuiKeys.XPositionInput],
                                                    y_pos=self._window[GuiKeys.YPositionInput])
        self._script_global_hotkeys.record_towers_position()

        self._selected_file_path: str = None
        self._activity_container = ActivityContainer()

        event, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo]))

        self._gui_updater = GuiUpdater(window=self._window, metadata=self._metadata)

        self.handle_viewed_towers(event=event, values=values)

    def _add_hotkey_binds(self):
        self._window.bind("<Control-o>", GuiMenu.File.Import)
        self._window.bind("<Control-s>", GuiMenu.File.Save)
        self._window.bind("<Control-Shift-S>", GuiMenu.File.SaveAs)

        self._window.bind("<Control_L>1", GuiMenu.ViewedTowers.All)
        self._window.bind("<Control_L>2", GuiMenu.ViewedTowers.Primary)
        self._window.bind("<Control_L>3", GuiMenu.ViewedTowers.Military)
        self._window.bind("<Control_L>4", GuiMenu.ViewedTowers.Magic)
        self._window.bind("<Control_L>5", GuiMenu.ViewedTowers.Support)

    def run(self):
        callback_map = self.get_callback_map()
        self._add_hotkey_binds()
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
        self._gui_updater.update_difficulty()

    def handle_change_hero(self, event: EventType, values: ValuesType):
        self._metadata.hero_type = GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo])
        self._gui_updater.update_hero()

    def handle_select_tower_type(self, event: EventType, values: ValuesType):
        try:
            tower_name = GuiParsers.parse_selected_tower(values[GuiKeys.TowerTypesListBox][0])
            self._gui_updater.update_selected_tower_type(selected_tower_text=tower_name)
        except ValueError:
            sg.popup("You must only select 1 tower type")

    def handle_select_existing_tower(self, event: EventType, values: ValuesType):
        try:
            selected_tower_value = GuiParsers.parse_existing_tower(values[GuiKeys.ExistingTowersListBox][0])
            self._gui_updater.update_selected_existing_tower(is_hero="Hero" in selected_tower_value)

        except IndexError:
            pass

    # noinspection PyMethodMayBeStatic
    def handle_keyboard_mouse(self, event: EventType, values: ValuesType):
        os.system("start ms-settings:easeofaccess-mouse")

    def handle_save_tower(self, event: EventType, values: ValuesType):
        if not are_values_set(values, GuiKeys.NewTowerTypeInput, GuiKeys.XPositionInput, GuiKeys.YPositionInput):
            sg.popup("You didn't fill all of the data!")
            return

        selected_script_entry_index = get_last_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        entry_index_to_select = None if selected_script_entry_index is None else selected_script_entry_index + 1
        if "Hero" == values[GuiKeys.NewTowerTypeInput]:
            if not self._activity_container.is_hero_placeable():
                sg.popup("Your Hero is already placed!")
                return

            self._activity_container.add_hero(name=values[GuiKeys.NewTowerTypeInput],
                                              x=int(values[GuiKeys.XPositionInput]),
                                              y=int(values[GuiKeys.YPositionInput]),
                                              index=entry_index_to_select)

        else:
            self._activity_container.add_new_tower(name=values[GuiKeys.NewTowerTypeInput],
                                                   x=int(values[GuiKeys.XPositionInput]),
                                                   y=int(values[GuiKeys.YPositionInput]),
                                                   index=entry_index_to_select)

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=entry_index_to_select)

    def handle_tower_modification(self, event: EventType, values: ValuesType):
        selected_towers_list = values[GuiKeys.ExistingTowersListBox]
        if len(selected_towers_list) != 1:
            sg.popup("You must chose exactly one tower!")
            return

        selected_tower_id = GuiParsers.parse_selected_tower_id(selected_towers_list[0])
        upgrade_tiers_map = {GuiKeys.TopUpgradeButton: UpgradeTier.top, GuiKeys.MiddleUpgradeButton: UpgradeTier.middle,
                             GuiKeys.BottomUpgradeButton: UpgradeTier.bottom}
        selected_script_entry_index = get_last_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        entry_index_to_select = None if not selected_script_entry_index else selected_script_entry_index + 1

        if event in upgrade_tiers_map:
            try:
                self._activity_container.upgrade_tower(tower_id=selected_tower_id, tier=upgrade_tiers_map[event],
                                                       index=entry_index_to_select)
            except ValueError:
                sg.popup("Tower is already at max level!")
                return

        elif event == GuiKeys.SellButton:
            try:
                self._activity_container.sell_tower(tower_id=selected_tower_id, index=entry_index_to_select)
            except ValueError:
                sg.popup("The tower is already sold!")
                return
        elif event == GuiKeys.TargetingButton:
            self._activity_container.change_targeting(tower_id=selected_tower_id, index=entry_index_to_select)
        elif event == GuiKeys.SpecialTargetingButton:
            self._activity_container.change_special_targeting(tower_id=selected_tower_id,
                                                              index=entry_index_to_select)
        elif event == GuiKeys.ModifyTowerButton:
            with self._script_global_hotkeys.pause_capture():
                x, y = popup_get_position(title=f"Modify position for tower: {selected_tower_id}")
                self._activity_container.change_position(tower_id=selected_tower_id, x=x, y=y)
        elif event == GuiKeys.DeleteTowerButton:
            self._activity_container.delete_tower(tower_id=selected_tower_id)
        else:
            raise RuntimeError

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=entry_index_to_select)

    def handle_delete_from_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to remove!")
            return

        selected_indexes = get_selected_indexes_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        for selected_entry_index in selected_indexes:
            self._activity_container.delete_entry(selected_entry_index)

        index_to_select = selected_indexes[0] if len(selected_indexes) == 1 else None
        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=index_to_select)

    def handle_move_up_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_indexes = get_selected_indexes_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        for selected_entry_index in selected_indexes:
            # Order of iteration is important to ensure all items can move up.
            try:
                self._activity_container.move_script_entry_up(entry_index=selected_entry_index)
            except ValueError:
                sg.popup("Item already first!")
                return

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=[i - 1 for i in selected_indexes])

    def handle_move_down_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_indexes = get_selected_indexes_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        for selected_entry_index in selected_indexes[::-1]:
            # Going in reverse to ensure that the last entry is valid to move
            try:
                self._activity_container.move_script_entry_down(entry_index=selected_entry_index)
            except ValueError:
                sg.popup("Item already last!")
                return

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container,
                                                            selected_script_index=[i + 1 for i in selected_indexes])

    def handle_save_button(self, event: EventType, values: ValuesType):
        if not self._metadata.hero_type:  # TODO: support not giving a hero if it is not used
            sg.popup("You must select a hero!")
            return

        if not self._selected_file_path:
            file_path = sg.popup_get_file("Please select file to import", default_path=get_files_dir(),
                                          file_types=(("Json files", "json"),))
            self._selected_file_path = file_path

        with open(self._selected_file_path, "w") as of:
            json.dump(Script(metadata=self._metadata, script=self._activity_container.script_container), of,
                      default=pydantic_encoder)

    def handle_import_button(self, event: EventType, values: ValuesType):

        self._selected_file_path = sg.popup_get_file("Please select file to import", default_path=get_files_dir(),
                                                     file_types=(("Json files", "json"),))

        with open(self._selected_file_path, "r") as of:
            json_dict = json.load(of)

        loaded_metadata = parse_metadata(json_dict=json_dict)
        self._metadata.difficulty = loaded_metadata.difficulty
        self._gui_updater.update_selected_difficulty()
        self._metadata.hero_type = loaded_metadata.hero_type
        self._gui_updater.update_selected_hero()

        self._activity_container.script_container = import_script(script_dict=json_dict["script"])
        self._activity_container.towers_container = parse_towers_from_script(
            script_entries=self._activity_container.script_container,
            metadata=self._metadata)

        self._gui_updater.update_existing_towers_and_script(activity_container=self._activity_container)

    def handle_viewed_towers(self, event: EventType, values: ValuesType):
        if GuiMenu.ViewedTowers.Primary == event:
            self._gui_updater.update_tower_types(towers_filter=lambda x: x.type == TowerType.Primary)
        elif GuiMenu.ViewedTowers.Military == event:
            self._gui_updater.update_tower_types(towers_filter=lambda x: x.type == TowerType.Military)
        elif GuiMenu.ViewedTowers.Magic == event:
            self._gui_updater.update_tower_types(towers_filter=lambda x: x.type == TowerType.Magic)
        elif GuiMenu.ViewedTowers.Support == event:
            self._gui_updater.update_tower_types(towers_filter=lambda x: x.type == TowerType.Support)
        else:
            self._gui_updater.update_tower_types(towers_filter=lambda x: True)

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty,
            GuiKeys.HeroCombo: self.handle_change_hero,
            GuiKeys.TowerTypesListBox: self.handle_select_tower_type,
            GuiKeys.ExistingTowersListBox: self.handle_select_existing_tower,
            GuiKeys.KeyboardMouseButton: self.handle_keyboard_mouse,
            GuiKeys.SaveTowerButton: self.handle_save_tower,
            **{
                i: self.handle_tower_modification for i in (
                    GuiKeys.TopUpgradeButton, GuiKeys.MiddleUpgradeButton, GuiKeys.BottomUpgradeButton,
                    GuiKeys.SellButton, GuiKeys.TargetingButton, GuiKeys.SpecialTargetingButton,
                    GuiKeys.ModifyTowerButton, GuiKeys.DeleteTowerButton)},
            GuiKeys.DeleteFromScriptButton: self.handle_delete_from_script,
            GuiKeys.MoveUpInScriptButton: self.handle_move_up_on_script,
            GuiKeys.MoveDownInScriptButton: self.handle_move_down_on_script,
            GuiMenu.File.Save: self.handle_save_button,
            GuiMenu.File.Import: self.handle_import_button,
            **{
                i: self.handle_viewed_towers for i in (
                    GuiMenu.ViewedTowers.All, GuiMenu.ViewedTowers.Primary, GuiMenu.ViewedTowers.Military,
                    GuiMenu.ViewedTowers.Magic, GuiMenu.ViewedTowers.Support)}
        }
