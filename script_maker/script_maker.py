from dataclasses import dataclass
import itertools
import json
from typing import List, Dict, Any

import PySimpleGUI as sg
from ahk import AHK

from common.cost.cost_parsing import TOWER_COSTS
from common.enums import UpgradeTier, Difficulty
from common.script.script_dataclasses import UpgradeAction, SellAction, ChangeTargetingAction, \
    ChangeSpecialTargetingAction, CreateAction, IAction
from common.tower import Tower
from hotkeys import Hotkeys


class GuiKeys:
    DifficultyListBox = "-difficulty-"
    TowerTypesListBox = "-chosen_tower_type-"
    ExistingTowersListBox = "-existing_towers-"
    XPositionInput = "-xpos-"
    YPositionInput = "-ypos-"
    NewTowerTypeInput = "-new_tower_type_input-"
    SaveTowerButton = '-save_tower_button-'
    ExistingTowerName = "-existing_tower_name-"
    TopUpgradeButton = "-top_upgrade_button-"
    MiddleUpgradeButton = "-middle_upgrade_button-"
    BottomUpgradeButton = "-bottom_upgrade_button-"
    SellButton = "-sell_button-"
    TargetingButton = "-targeting_button-"
    SpecialTargetingButton = "-s_targeting_button-"
    ExportButton = "-export_button-"
    ScriptBox = "-script_box-"


DIFFICULTY_MAP = {"easy": Difficulty.easy, "medium": Difficulty.medium,
                  "hard": Difficulty.hard, "chimps": Difficulty.chimps}


def get_layout() -> List[List[Any]]:
    left_col = [
        [sg.Text("Choose difficulty", size=(20, 1), font="Lucida", justification="left")],
        [sg.Combo(list(DIFFICULTY_MAP.keys()), default_value=list(DIFFICULTY_MAP.keys())[0],
                  key=GuiKeys.DifficultyListBox, enable_events=True)],
        [sg.Text("Towers", size=(30, 1), font="Lucida", justification="left")],
        [sg.Listbox(values=get_tower_options(),
                    select_mode="extended", key=GuiKeys.TowerTypesListBox, size=(30, 25), enable_events=True),
         sg.Listbox(values=[],
                    select_mode="extended", key=GuiKeys.ExistingTowersListBox, size=(75, 25), enable_events=True),
         ]
    ]

    right_col = [
        [sg.Text("Click Ctrl + Shift + R to capture mouse position.")],
        [
            sg.Text("X"),
            sg.In(size=(5, 1), enable_events=True, key=GuiKeys.XPositionInput),
            sg.Text("Y"),
            sg.In(size=(5, 1), enable_events=True, key=GuiKeys.YPositionInput)
        ],
        [sg.Text("Type:"),
         sg.In(size=(40, 1), disabled=True, key=GuiKeys.NewTowerTypeInput)],
        [sg.Button("Save", enable_events=True, key=GuiKeys.SaveTowerButton)],
        [sg.HSeparator()],
        [sg.Text("Existing tower upgrades")],
        [sg.Text("Type:"),
         sg.In(size=(40, 1), disabled=True, key=GuiKeys.ExistingTowerName)],
        [
            sg.Button("Upgrade Top", size=(15, 1), enable_events=True, key=GuiKeys.TopUpgradeButton),
            sg.Button("Upgrade Middle", size=(15, 1), enable_events=True, key=GuiKeys.MiddleUpgradeButton),
            sg.Button("Upgrade Bottom", size=(15, 1), enable_events=True, key=GuiKeys.BottomUpgradeButton)
        ],
        [
            sg.Button("Sell", size=(15, 1), enable_events=True, key=GuiKeys.SellButton),
            sg.Button("Targeting", size=(15, 1), enable_events=True, key=GuiKeys.TargetingButton),
            sg.Button("S. Targeting", size=(15, 1), enable_events=True, key=GuiKeys.SpecialTargetingButton)
        ],
        [sg.HSeparator()],
        [sg.Button("Export", size=(15, 1), enable_events=True, key=GuiKeys.ExportButton)]
    ]

    script_layout = [[sg.Text("Script:")],
                     [sg.Listbox(values=[], select_mode="extended", key=GuiKeys.ScriptBox, size=(150, 12),
                                 enable_events=True)]]

    return [[sg.Column(left_col),
             sg.VSeparator(),
             sg.Column(right_col)],
            script_layout]


@dataclass
class AdditionalTowerInfo:
    sold: bool = False
    targeting: int = 0
    s_targeting: int = 0


def get_tower_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
    return [f"{name}: {cost.base_cost.get_mapping()[difficulty]}$" for name, cost in TOWER_COSTS.items()]


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


def get_additional_information(tower_id: int, d: Dict[int, AdditionalTowerInfo]):
    if tower_id not in d:
        d[tower_id] = AdditionalTowerInfo()

    return d[tower_id]


def update_towers_from_list(exiting_towers: sg.Listbox, towers_list: Dict[int, Tower],
                            additional_info: Dict[int, AdditionalTowerInfo]):
    exiting_towers.update(get_existing_towers(towers_list, additional_info), set_to_index=exiting_towers.get_indexes())


def update_script_box(script_box: sg.Listbox, script_list: List[Dict[str, Any]]):
    output = []
    for action in script_list:
        if isinstance(action, CreateAction):
            output.append(f"Create: {action.name}({action.id}) | X: {action.x} Y: {action.y}")
        elif isinstance(action, UpgradeAction):
            output.append(f"Upgrade: ({action.id}) | tier: {action.tier}")
        elif isinstance(action, SellAction):
            output.append(f"Sell: ({action.id})")
        elif isinstance(action, ChangeTargetingAction):
            output.append(f"Change targeting: ({action.id})")
        elif isinstance(action, ChangeSpecialTargetingAction):
            output.append(f"Change special targeting: ({action.id})")

    script_box.update(output, )


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IAction):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)


class GuiHandlers:
    def __init__(self, window: sg.Window):
        self._window = window

        self._towers_list: Dict[int, Tower] = {}
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
        self._script = []
        self._difficulty = Difficulty.easy
        self._id_generator = itertools.count()

    def handle_change_difficulty(self, event: Dict[str, Any], values: List[Any]):
        difficulty_value = values[GuiKeys.DifficultyListBox]
        self._difficulty = DIFFICULTY_MAP[difficulty_value]
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(self._difficulty), )

    def handle_select_tower_type(self, event: Dict[str, Any], values: List[Any]):
        try:
            self._window[GuiKeys.NewTowerTypeInput].update(values[GuiKeys.TowerTypesListBox][0].split(":")[0], )
        except IndexError:
            pass

    def handle_select_existing_tower(self, event: Dict[str, Any], values: List[Any]):
        try:
            self._window[GuiKeys.ExistingTowerName].update(values[GuiKeys.ExistingTowersListBox][0].split("|")[0], )
        except IndexError:
            pass

    def handle_save_tower(self, event: Dict[str, Any], values: List[Any]):
        if not values[GuiKeys.NewTowerTypeInput] or not values[GuiKeys.XPositionInput] \
                or not values[GuiKeys.YPositionInput]:
            sg.popup("You didn't fill all of the data!")
            return

        tower_id = next(self._id_generator)
        new_tower = Tower(name=values[GuiKeys.NewTowerTypeInput],
                          x=int(values[GuiKeys.XPositionInput]),
                          y=int(values[GuiKeys.YPositionInput]))
        self._towers_list[tower_id] = new_tower
        update_towers_from_list(self._window[GuiKeys.ExistingTowersListBox], self._towers_list,
                                self._additional_tower_information)
        self._script.append(CreateAction(name=new_tower.name, id=tower_id, x=new_tower.x, y=new_tower.y))
        update_script_box(script_box=self._window[GuiKeys.ScriptBox], script_list=self._script)

    def handle_tower_modification(self, event: Dict[str, Any], values: List[Any]):
        if not values[GuiKeys.ExistingTowerName]:
            sg.popup("You must chose a tower first!")
            return

        selected_tower_id = int(values[GuiKeys.ExistingTowersListBox][0].split(":")[0])
        if event == GuiKeys.TopUpgradeButton:
            self._towers_list[selected_tower_id].tier_map[UpgradeTier.top] += 1  # TODO: overflow
            action = UpgradeAction(id=selected_tower_id, tier=UpgradeTier.top)
        elif event == GuiKeys.MiddleUpgradeButton:
            self._towers_list[selected_tower_id].tier_map[UpgradeTier.middle] += 1  # TODO: overflow
            action = UpgradeAction(id=selected_tower_id, tier=UpgradeTier.middle)
        elif event == GuiKeys.BottomUpgradeButton:
            self._towers_list[selected_tower_id].tier_map[UpgradeTier.bottom] += 1  # TODO: overflow
            action = UpgradeAction(id=selected_tower_id, tier=UpgradeTier.bottom)
        elif event == GuiKeys.SellButton:
            # TODO: warn about updating sold towers
            get_additional_information(selected_tower_id, self._additional_tower_information).sold = True
            action = SellAction(id=selected_tower_id)
        elif event == GuiKeys.TargetingButton:
            # TODO: overflow
            get_additional_information(selected_tower_id, self._additional_tower_information).targeting += 1
            action = ChangeTargetingAction(id=selected_tower_id)
        elif event == GuiKeys.SpecialTargetingButton:
            # TODO: overflow
            get_additional_information(selected_tower_id, self._additional_tower_information).s_targeting += 1
            action = ChangeSpecialTargetingAction(id=selected_tower_id)
        else:
            raise RuntimeError

        self._script.append(action)
        update_towers_from_list(self._window[GuiKeys.ExistingTowersListBox], self._towers_list,
                                self._additional_tower_information)
        update_script_box(self._window[GuiKeys.ScriptBox], self._script)

    def handle_export_button(self, event: Dict[str, Any], values: List[Any]):
        with open("../exported.json", "w") as of:  # TODO: move to actual path
            json.dump({"metadata": {"difficulty": self._difficulty.value}, "script": self._script}, of,
                      cls=ComplexEncoder)


def main():
    window = sg.Window(title="BTD Scripter", layout=get_layout())
    Hotkeys(ahk=AHK(), x_pos=window[GuiKeys.XPositionInput], y_pos=window[GuiKeys.YPositionInput])

    gui_handler = GuiHandlers(window=window)

    while True:
        event, values = window.read()

        if event == GuiKeys.DifficultyListBox:
            gui_handler.handle_change_difficulty(event=event, values=values)
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
