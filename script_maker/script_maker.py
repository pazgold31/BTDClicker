import itertools
import json
from typing import List, Dict, Any

import PySimpleGUI as sg
from ahk import AHK

from common.cost.cost_parsing import TOWER_COSTS
from common.enums import UpgradeTier, Difficulty
from common.script.script_dataclasses import UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, \
    ChangeSpecialTargetingEntry, CreateTowerEntry, IScriptEntry, GameMetadata
from common.tower import Tower
from hotkeys import Hotkeys
from additional_tower_info import AdditionalTowerInfo, get_additional_information
from gui import GuiKeys, DIFFICULTY_MAP, get_layout, get_tower_options, get_hero_options


def is_tier_upgradeable(tower: Tower, tier: UpgradeTier) -> bool:
    current_upgrade = tower.tier_map[tier]
    try:
        new_cost = TOWER_COSTS[tower.name].upgrades.get_mapping()[tier].get_mapping()[current_upgrade + 1]
        return new_cost
    except KeyError:
        return False


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


class ScriptJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IScriptEntry) or isinstance(obj, GameMetadata):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)


class GuiHandlers:
    def __init__(self, window: sg.Window):
        self._window = window

        self._towers_list: Dict[int, Tower] = {}
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
        self._script: List[IScriptEntry] = []
        self._metadata = GameMetadata(Difficulty.easy, None)
        self._id_generator = itertools.count()

    def handle_change_difficulty(self, event: Dict[str, Any], values: List[Any]):
        difficulty_value = values[GuiKeys.DifficultyListBox]
        self._metadata.difficulty = DIFFICULTY_MAP[difficulty_value]
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(self._metadata.difficulty,
                                                                         chosen_hero=self._metadata.hero_type), )
        selected_hero_index = self._window[GuiKeys.HeroListBox].Values.index(values[GuiKeys.HeroListBox])
        hero_options = get_hero_options(self._metadata.difficulty)
        self._window[GuiKeys.HeroListBox].update(values=hero_options, value=hero_options[selected_hero_index])

    def handle_change_hero(self, event: Dict[str, Any], values: List[Any]):
        self._metadata.hero_type = values[GuiKeys.HeroListBox].split(":")[0]
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(self._metadata.difficulty), )
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(self._metadata.difficulty,
                                                                         chosen_hero=self._metadata.hero_type), )

    def handle_select_tower_type(self, event: Dict[str, Any], values: List[Any]):
        try:
            tower_name = values[GuiKeys.TowerTypesListBox][0].split(":")[0]
            selected_tower_text = "Hero" if "Hero" in tower_name else tower_name
            self._window[GuiKeys.NewTowerTypeInput].update(selected_tower_text, )
        except IndexError:
            pass

    def handle_select_existing_tower(self, event: Dict[str, Any], values: List[Any]):
        try:
            selected_tower_value = values[GuiKeys.ExistingTowersListBox][0].split("|")[0]
            self._window[GuiKeys.ExistingTowerName].update(selected_tower_value, )
            is_hero = "Hero" in selected_tower_value
            self._window[GuiKeys.TopUpgradeButton].update(disabled=is_hero)
            self._window[GuiKeys.MiddleUpgradeButton].update(disabled=is_hero)
            self._window[GuiKeys.BottomUpgradeButton].update(disabled=is_hero)
        except IndexError:
            pass

    def handle_save_tower(self, event: Dict[str, Any], values: List[Any]):
        if not values[GuiKeys.NewTowerTypeInput] or not values[GuiKeys.XPositionInput] \
                or not values[GuiKeys.YPositionInput]:
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

    def _handle_tower_upgrade(self, tower_id: int, tier: UpgradeTier) -> IScriptEntry:
        if not is_tier_upgradeable(tower=self._towers_list[tower_id], tier=tier):
            sg.popup("The tower is at max level!")

        self._towers_list[tower_id].tier_map[tier] += 1
        return UpgradeTowerEntry(id=tower_id, tier=tier)

    def handle_tower_modification(self, event: Dict[str, Any], values: List[Any]):
        if not values[GuiKeys.ExistingTowerName]:
            sg.popup("You must chose a tower first!")
            return

        selected_tower_id = int(values[GuiKeys.ExistingTowersListBox][0].split(":")[0])
        if event == GuiKeys.TopUpgradeButton:
            action = self._handle_tower_upgrade(tower_id=selected_tower_id, tier=UpgradeTier.top)
        elif event == GuiKeys.MiddleUpgradeButton:
            action = self._handle_tower_upgrade(tower_id=selected_tower_id, tier=UpgradeTier.middle)
        elif event == GuiKeys.BottomUpgradeButton:
            action = self._handle_tower_upgrade(tower_id=selected_tower_id, tier=UpgradeTier.bottom)
        elif event == GuiKeys.SellButton:
            additional_tower_info = get_additional_information(selected_tower_id, self._additional_tower_information)
            if additional_tower_info.sold:
                sg.popup("The tower is already sold!")
                return

            additional_tower_info.sold = True
            action = SellTowerEntry(id=selected_tower_id)
        elif event == GuiKeys.TargetingButton:
            get_additional_information(selected_tower_id, self._additional_tower_information).targeting += 1
            action = ChangeTargetingEntry(id=selected_tower_id)
        elif event == GuiKeys.SpecialTargetingButton:
            get_additional_information(selected_tower_id, self._additional_tower_information).s_targeting += 1
            action = ChangeSpecialTargetingEntry(id=selected_tower_id)
        else:
            raise RuntimeError

        self._script.append(action)
        update_towers_from_list(self._window[GuiKeys.ExistingTowersListBox], self._towers_list,
                                self._additional_tower_information)
        update_script_box(self._window[GuiKeys.ScriptBox], self._script)

    def handle_export_button(self, event: Dict[str, Any], values: List[Any]):
        if not self._metadata.hero_type:
            sg.popup("You must select a hero!")
            return

        with open("../exported.json", "w") as of:  # TODO: move to actual path
            json.dump({"metadata": self._metadata, "script": self._script}, of,
                      cls=ScriptJsonEncoder)


def main():
    window = sg.Window(title="BTD Scripter", layout=get_layout())
    Hotkeys(ahk=AHK(), x_pos=window[GuiKeys.XPositionInput], y_pos=window[GuiKeys.YPositionInput])

    gui_handler = GuiHandlers(window=window)

    while True:
        event, values = window.read()

        if event == GuiKeys.DifficultyListBox:
            gui_handler.handle_change_difficulty(event=event, values=values)
            continue

        if event == GuiKeys.HeroListBox:
            gui_handler.handle_change_hero(event=event, values=values)
            continue

        if event == GuiKeys.TowerTypesListBox:
            gui_handler.handle_select_tower_type(event=event, values=values)
            continue

        if event == GuiKeys.ExistingTowersListBox:
            gui_handler.handle_select_existing_tower(event=event, values=values)
            continue

        if event == GuiKeys.SaveTowerButton:
            gui_handler.handle_save_tower(event=event, values=values)
            continue

        if event in (GuiKeys.TopUpgradeButton, GuiKeys.MiddleUpgradeButton, GuiKeys.BottomUpgradeButton,
                     GuiKeys.SellButton, GuiKeys.TargetingButton, GuiKeys.SpecialTargetingButton):
            gui_handler.handle_tower_modification(event=event, values=values)
            continue

        if event == GuiKeys.ExportButton:
            gui_handler.handle_export_button(event=event, values=values)

        if event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    main()
