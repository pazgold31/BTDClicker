import json
import os
from typing import Dict
import PySimpleGUI as sg
from ahk import AHK
from pydantic.json import pydantic_encoder

from common.enums import UpgradeTier
from common.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.tower import BaseTower
from script_maker.script.activity_container import ActivityContainer
from common.script.script_dataclasses import GameMetadata, Script
from script_maker.gui.gui_controls_utils import are_values_set, get_selected_index_for_list_box
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_types import EventType, ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater
from script_maker.hotkeys import Hotkeys


class GuiClass:
    def __init__(self, ):
        self._window = sg.Window(title="BTD6 Scripter", layout=get_layout())
        Hotkeys(ahk=AHK(), x_pos=self._window[GuiKeys.XPositionInput], y_pos=self._window[GuiKeys.YPositionInput])

        self._activity_container = ActivityContainer()

        event, values = self._window.read(0)
        self._metadata = GameMetadata(difficulty=DIFFICULTY_MAP[values[GuiKeys.DifficultyListBox]],
                                      hero_type=GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo]))

        self._gui_updater = GuiUpdater(window=self._window, metadata=self._metadata)

    def run(self):
        callback_map = self.get_callback_map()
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
        self._gui_updater.update_difficulty(values=values)

    def handle_change_hero(self, event: EventType, values: ValuesType):
        self._metadata.hero_type = GuiParsers.parse_selected_hero(values[GuiKeys.HeroCombo])
        self._gui_updater.update_hero()

    def handle_select_tower_type(self, event: EventType, values: ValuesType):
        try:
            tower_name = GuiParsers.parse_selected_tower(values[GuiKeys.TowerTypesListBox][0])
            self._gui_updater.update_selected_tower_type(selected_tower_text=tower_name, values=values)
        except IndexError:
            pass

    def handle_select_existing_tower(self, event: EventType, values: ValuesType):
        try:
            selected_tower_value = GuiParsers.parse_existing_tower(values[GuiKeys.ExistingTowersListBox][0])
            self._gui_updater.update_selected_existing_tower(selected_tower_text=selected_tower_value,
                                                             is_hero="Hero" in selected_tower_value)

        except IndexError:
            pass

    def handle_keyboard_mouse(self, event: EventType, values: ValuesType):
        os.system("start ms-settings:easeofaccess-mouse")

    def handle_save_tower(self, event: EventType, values: ValuesType):
        if not are_values_set(values, GuiKeys.NewTowerTypeInput, GuiKeys.XPositionInput, GuiKeys.YPositionInput):
            sg.popup("You didn't fill all of the data!")
            return

        selected_script_entry_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)

        if "Hero" == values[GuiKeys.NewTowerTypeInput]:
            if not self._activity_container.is_hero_placeable():
                sg.popup("Your Hero is already placed!")
                return

            self._activity_container.add_hero(name=values[GuiKeys.NewTowerTypeInput],
                                              x=int(values[GuiKeys.XPositionInput]),
                                              y=int(values[GuiKeys.YPositionInput]),
                                              index=selected_script_entry_index + 1)

        else:
            self._activity_container.add_new_tower(name=values[GuiKeys.NewTowerTypeInput],
                                                   x=int(values[GuiKeys.XPositionInput]),
                                                   y=int(values[GuiKeys.YPositionInput]),
                                                   index=selected_script_entry_index + 1)

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container,
                                                            selected_script_index=selected_script_entry_index + 1)

    def handle_tower_modification(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ExistingTowersListBox]:
            sg.popup("You must chose a tower first!")
            return

        selected_tower_id = GuiParsers.parse_selected_tower_id(values[GuiKeys.ExistingTowersListBox][0])
        upgrade_tiers_map = {GuiKeys.TopUpgradeButton: UpgradeTier.top, GuiKeys.MiddleUpgradeButton: UpgradeTier.middle,
                             GuiKeys.BottomUpgradeButton: UpgradeTier.bottom}
        selected_script_entry_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)

        if event in upgrade_tiers_map:
            try:
                self._activity_container.upgrade_tower(tower_id=selected_tower_id, tier=upgrade_tiers_map[event],
                                                       index=selected_script_entry_index + 1)
            except ValueError:
                sg.popup("Tower is already at max level!")
                return

        elif event == GuiKeys.SellButton:
            try:
                self._activity_container.sell_tower(tower_id=selected_tower_id, index=selected_script_entry_index + 1)
            except ValueError:
                sg.popup("The tower is already sold!")
                return
        elif event == GuiKeys.TargetingButton:
            self._activity_container.change_targeting(tower_id=selected_tower_id, index=selected_script_entry_index + 1)
        elif event == GuiKeys.SpecialTargetingButton:
            self._activity_container.change_special_targeting(tower_id=selected_tower_id,
                                                              index=selected_script_entry_index + 1)
        else:
            raise RuntimeError

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container,
                                                            selected_script_index=selected_script_entry_index + 1)

    def handle_delete_from_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to remove!")
            return

        selected_entry_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        self._activity_container.delete_entry(selected_entry_index)

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container,
                                                            selected_script_index=selected_entry_index)

    def handle_move_up_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_entry_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        try:
            self._activity_container.move_script_entry_up(entry_index=selected_entry_index)
        except ValueError:
            sg.popup("Item already first!")
            return

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container,
                                                            selected_script_index=selected_entry_index - 1)

    def handle_move_down_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_entry_index = get_selected_index_for_list_box(window=self._window, key=GuiKeys.ScriptBox)
        try:
            self._activity_container.move_script_entry_down(entry_index=selected_entry_index)
        except ValueError:
            sg.popup("Item already last!")
            return

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container,
                                                            selected_script_index=selected_entry_index + 1)

    def handle_export_button(self, event: EventType, values: ValuesType):
        if not self._metadata.hero_type:  # TODO: support not giving a hero if it is not used
            sg.popup("You must select a hero!")
            return

        with open("../exported.json", "w") as of:  # TODO: move to actual path
            json.dump(Script(metadata=self._metadata, script=self._activity_container.script_container), of,
                      default=pydantic_encoder)

    def handle_import_button(self, event: EventType, values: ValuesType):
        with open("../exported.json", "r") as of:  # TODO: move to actual path
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

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

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
                    GuiKeys.SellButton, GuiKeys.TargetingButton, GuiKeys.SpecialTargetingButton)},
            GuiKeys.DeleteFromScriptButton: self.handle_delete_from_script,
            GuiKeys.MoveUpInScriptButton: self.handle_move_up_on_script,
            GuiKeys.MoveDownInScriptButton: self.handle_move_down_on_script,
            GuiKeys.ExportButton: self.handle_export_button,
            GuiKeys.ImportButton: self.handle_import_button
        }
