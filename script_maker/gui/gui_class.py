import itertools
import os
from typing import Dict, List, Any
import PySimpleGUI as sg
from ahk import AHK

from common.enums import UpgradeTier
from common.script.script_dataclasses import IScriptEntry, GameMetadata, CreateTowerEntry, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry
from common.tower import Tower
from script_maker.additional_tower_info import AdditionalTowerInfo
from script_maker.gui.gui_controls_utils import are_values_set
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_layout, DIFFICULTY_MAP
from script_maker.gui.gui_parsers import GuiParsers
from script_maker.gui.gui_types import EventType, ValuesType, CallbackMethod
from script_maker.gui.gui_updater import GuiUpdater
from script_maker.hotkeys import Hotkeys


def convert_targeting(targeting: int) -> str:
    # TODO: support elite targeting and such
    targeting = targeting % 4
    return "First" if targeting == 0 else "Last" if targeting == 1 else "Close" if \
        targeting == 2 else "Strong"


def get_existing_towers(towers: Dict[int, Tower], additional_info: Dict[int, AdditionalTowerInfo]) -> List[str]:
    return [
        f"{tower_id}: {tower.name} | x:{tower.x} y:{tower.y} | {tower.tier_map[UpgradeTier.top]}-"
        f"{tower.tier_map[UpgradeTier.middle]}-{tower.tier_map[UpgradeTier.bottom]} | "
        f"Targeting: {convert_targeting(additional_info.get(tower_id, AdditionalTowerInfo()).targeting)} | "
        f"S.Targeting: {additional_info.get(tower_id, AdditionalTowerInfo()).s_targeting}"
        f"{' SOLD' if additional_info.get(tower_id, AdditionalTowerInfo()).sold else ''}" for
        tower_id, tower in towers.items()]


def update_towers_from_list(exiting_towers: sg.Listbox, towers_list: Dict[int, Tower],
                            additional_info: Dict[int, AdditionalTowerInfo]):
    exiting_towers.update(get_existing_towers(towers_list, additional_info), set_to_index=exiting_towers.get_indexes())


def update_script_box(script_box: sg.Listbox, script_list: List[Dict[str, Any]]):
    output = []
    for action in script_list:
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

    script_box.update(output, )


class GuiClass:
    def __init__(self, ):
        self._window = sg.Window(title="BTD6 Scripter", layout=get_layout())
        Hotkeys(ahk=AHK(), x_pos=self._window[GuiKeys.XPositionInput], y_pos=self._window[GuiKeys.YPositionInput])

        self._towers_list: Dict[int, Tower] = {}
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
        self._script: List[IScriptEntry] = []
        self._id_generator = itertools.count()

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
            self._gui_updater.update_selected_existing_tower(values=values, selected_tower_text=selected_tower_value,
                                                             is_hero="Hero" in selected_tower_value)

        except IndexError:
            pass

    def handle_keyboard_mouse(self, event: EventType, values: ValuesType):
        os.system("start ms-settings:easeofaccess-mouse")

    def handle_save_tower(self, event: EventType, values: ValuesType):
        if not are_values_set(values, GuiKeys.NewTowerTypeInput, GuiKeys.XPositionInput, GuiKeys.YPositionInput):
            sg.popup("You didn't fill all of the data!")
            return

        if "Hero" == values[GuiKeys.NewTowerTypeInput] and \
                any(i for i in self._script if isinstance(i, CreateTowerEntry) and i.name == "Hero"):
            sg.popup("Your Hero is already placed!")
            return

        tower_id = next(self._id_generator)
        new_tower = Tower(name=values[GuiKeys.NewTowerTypeInput],
                          x=int(values[GuiKeys.XPositionInput]),
                          y=int(values[GuiKeys.YPositionInput]))
        self._towers_list[tower_id] = new_tower
        update_towers_from_list(self._window[GuiKeys.ExistingTowersListBox], self._towers_list,
                                self._additional_tower_information)
        self._script.append(CreateTowerEntry(name=new_tower.name, id=tower_id, x=new_tower.x, y=new_tower.y))
        update_script_box(script_box=self._window[GuiKeys.ScriptBox], script_list=self._script)

    def get_callback_map(self) -> Dict[str, CallbackMethod]:
        return {
            GuiKeys.DifficultyListBox: self.handle_change_difficulty,
            GuiKeys.HeroListBox: self.handle_change_hero,
            GuiKeys.TowerTypesListBox: self.handle_select_tower_type,
            GuiKeys.ExistingTowersListBox: self.handle_select_existing_tower,
            GuiKeys.KeyboardMouseButton: self.handle_keyboard_mouse,
            GuiKeys.SaveTowerButton: self.handle_save_tower
        }


def main():
    gui_class = GuiClass()
    gui_class.run()


if __name__ == '__main__':
    main()
