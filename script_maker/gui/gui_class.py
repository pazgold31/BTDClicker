import os
from typing import Dict
import PySimpleGUI as sg
from ahk import AHK

from common.enums import UpgradeTier
from script_maker.script.activity_container import ActivityContainer
from common.script.script_dataclasses import GameMetadata
from script_maker.gui.gui_controls_utils import are_values_set
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
                                      hero_type=GuiParsers.parse_selected_hero(values[GuiKeys.HeroListBox]))

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
        self._metadata.hero_type = GuiParsers.parse_selected_hero(values[GuiKeys.HeroListBox])
        self._gui_updater.update_hero(metadata=self._metadata)

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

        if "Hero" == values[GuiKeys.NewTowerTypeInput] and not self._activity_container.is_hero_placeable():
            sg.popup("Your Hero is already placed!")
            return

        self._activity_container.add_new_tower(name=values[GuiKeys.NewTowerTypeInput],
                                               x=int(values[GuiKeys.XPositionInput]),
                                               y=int(values[GuiKeys.YPositionInput]))

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

    def handle_tower_modification(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ExistingTowersListBox]:
            sg.popup("You must chose a tower first!")
            return

        selected_tower_id = GuiParsers.parse_selected_tower_id(values[GuiKeys.ExistingTowersListBox])
        upgrade_tiers_map = {GuiKeys.TopUpgradeButton: UpgradeTier.top, GuiKeys.MiddleUpgradeButton: UpgradeTier.middle,
                             GuiKeys.BottomUpgradeButton: UpgradeTier.bottom}
        if event in upgrade_tiers_map:
            try:
                self._activity_container.upgrade_tower(tower_id=selected_tower_id, tier=upgrade_tiers_map[event])
            except ValueError:
                sg.popup("Tower is already at max level!")
                return

        elif event == GuiKeys.SellButton:
            try:
                self._activity_container.sell_tower(tower_id=selected_tower_id)
            except ValueError:
                sg.popup("The tower is already sold!")
                return
        elif event == GuiKeys.TargetingButton:
            self._activity_container.change_targeting(tower_id=selected_tower_id)
        elif event == GuiKeys.SpecialTargetingButton:
            self._activity_container.change_special_targeting(tower_id=selected_tower_id)
        else:
            raise RuntimeError

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

    def handle_delete_from_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to remove!")
            return

        selected_entry_index = self._window[GuiKeys.ScriptBox].Values.index(values[GuiKeys.ScriptBox][0])
        self._activity_container.delete_entry(selected_entry_index)

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

    def handle_move_up_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_entry_index = self._window[GuiKeys.ScriptBox].Values.index(values[GuiKeys.ScriptBox][0])
        try:
            self._activity_container.move_script_entry_down(entry_index=selected_entry_index)
        except ValueError:
            sg.popup("Item already first!")
            return

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

    def handle_move_down_on_script(self, event: EventType, values: ValuesType):
        if not values[GuiKeys.ScriptBox]:
            sg.popup("You must select an entry to move!")
            return

        selected_entry_index = self._window[GuiKeys.ScriptBox].Values.index(values[GuiKeys.ScriptBox][0])
        try:
            self._activity_container.move_script_entry_down(entry_index=selected_entry_index)
        except ValueError:
            sg.popup("Item already last!")
            return

        self._gui_updater.update_existing_towers_and_script(values=values,
                                                            towers_container=self._activity_container.towers_container,
                                                            script_container=self._activity_container.script_container)

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty,
            GuiKeys.HeroListBox: self.handle_change_hero,
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
            GuiKeys.MoveDownInScriptButton: self.handle_move_down_on_script
        }


def main():
    gui_class = GuiClass()
    gui_class.run()


if __name__ == '__main__':
    main()
