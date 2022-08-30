from dataclasses import dataclass
import itertools
import json
from typing import List, Dict, Any

import PySimpleGUI as sg
from ahk import AHK

from common.cost_parser import TOWER_COSTS
from common.hotkeys import Hotkeys
from common.tower import Tower


def get_layout() -> List[List[Any]]:
    left_col = [

        [sg.Text("Choose difficulty", size=(20, 1), font="Lucida", justification="left")],
        [sg.Combo(["Easy", "Medium", "Hard", "Chimps"], default_value="Easy", key="difficulty", enable_events=True)],
        [sg.Text("Towers", size=(30, 1), font="Lucida", justification="left")],
        [sg.Listbox(values=get_monkey_options(),
                    select_mode="extended", key="chosen_monkey_type", size=(30, 25), enable_events=True),
         sg.Listbox(values=[],
                    select_mode="extended", key="exsiting_towers", size=(75, 25), enable_events=True),

         ]
    ]

    right_col = [
        [sg.Text("Click Ctrl + Shift + R to capture mouse position.")],
        [
            sg.Text("X"),
            sg.In(size=(5, 1), enable_events=True, key="x_pos"),
            sg.Text("Y"),
            sg.In(size=(5, 1), enable_events=True, key="y_pos")
        ],
        [sg.Text("Type:"),
         sg.In(size=(40, 1), disabled=True, key="new_monkey_name")],
        [sg.Button("Save", enable_events=True, key="save_button")],
        [sg.HSeparator()],
        [sg.Text("Existing Monkeys upgrades")],
        [sg.Text("Type:"),
         sg.In(size=(40, 1), disabled=True, key="existing_monkey_name")],
        [
            sg.Button("Upgrade Top", size=(15, 1), enable_events=True, key="top_upgrade_button"),
            sg.Button("Upgrade Middle", size=(15, 1), enable_events=True, key="middle_upgrade_button"),
            sg.Button("Upgrade Bottom", size=(15, 1), enable_events=True, key="bottom_upgrade_button")
        ],
        [
            sg.Button("Sell", size=(15, 1), enable_events=True, key="sell_button"),
            sg.Button("Targeting", size=(15, 1), enable_events=True, key="targeting_button"),
            sg.Button("S. Targeting", size=(15, 1), enable_events=True, key="s_targeting_button")
        ],
        [sg.HSeparator()],
        [sg.Button("Export", size=(15, 1), enable_events=True, key="export_button")]
    ]

    script_layout = [[sg.Text("Script:")],
                     [sg.Listbox(values=[], select_mode="extended", key="script_box", size=(150, 12),
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


def get_monkey_options(difficulty: str = "Easy") -> List[str]:
    return [f"{name}: {cost.base_cost.__getattribute__(difficulty.lower())}$" for name, cost in TOWER_COSTS.items()]


def convert_targeting(targeting: int):
    # TODO: support elite targeting and such
    return "First" if targeting == 0 else "Last" if targeting == 1 else "Close" if \
        targeting == 2 else "Strong" if targeting == 3 else "ERROR"


def get_existing_towers(towers: Dict[int, Tower], additional_info: Dict[int, AdditionalTowerInfo]) -> List[str]:
    return [f"{tower_id}: {tower.name} | x:{tower.x} y:{tower.y} | {tower.top}-{tower.middle}-{tower.bottom} | " \
            f"Targeting: {convert_targeting(additional_info.get(tower_id, AdditionalTowerInfo()).targeting)} | " \
            f"S.Targeting: {additional_info.get(tower_id, AdditionalTowerInfo()).s_targeting}" \
            f"{' SOLD' if additional_info.get(tower_id, AdditionalTowerInfo()).sold else ''}" for
            tower_id, tower in towers.items()]


def get_additional_information(tower_id: int, d: Dict[int, AdditionalTowerInfo]):
    if tower_id not in d:
        d[tower_id] = AdditionalTowerInfo()

    return d[tower_id]


def update_towers_from_list(exiting_towers: sg.Listbox, towers_list: Dict[int, Tower],
                            additional_info: Dict[int, AdditionalTowerInfo]):
    exiting_towers.update(get_existing_towers(towers_list, additional_info), set_to_index=exiting_towers.get_indexes())


def update_box_from_script(script_box: sg.Listbox, script_list: List[Dict[str, Any]]):
    output = []
    for line in script_list:
        if line["action"] == "create":
            output.append(f"Create: {line['name']}({line['id']}) | X: {line['x']} Y: {line['y']}")
        elif line["action"] == "upgrade":
            output.append(f"Upgrade: ({line['id']}) | tier: {line['tier']}")
        elif line["action"] == "sell":
            output.append(f"Sell: ({line['id']})")
        elif line["action"] == "change_targeting":
            output.append(f"Change targeting: ({line['id']})")
        elif line["action"] == "change_special_targeting":
            output.append(f"Change special targeting: ({line['id']})")

    script_box.update(output, )


def create_upgrade_action(tower_id: int, tier: int) -> Dict:
    return {
        "action": "upgrade",
        "id": tower_id,
        "tier": tier
    }


def create_modify_action(tower_id: int, action: str) -> Dict:
    return {
        "action": action,
        "id": tower_id,
    }


def main():
    towers_list: Dict[int, Tower] = {}
    additional_tower_information: Dict[int, AdditionalTowerInfo] = {}
    script = []
    id_generator = itertools.count()

    # sg.theme("DarkBlue")

    window = sg.Window(title="BTD Scripter", layout=get_layout())

    hkeys = Hotkeys(ahk=AHK(), x_pos=window["x_pos"], y_pos=window["y_pos"])
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button

        if event == "difficulty":
            window["chosen_monkey_type"].update(get_monkey_options(values["difficulty"]), )

        if event == "chosen_monkey_type":
            window["new_monkey_name"].update(values["chosen_monkey_type"][0].split(":")[0], )

        if event == "exsiting_towers":
            window["existing_monkey_name"].update(values["exsiting_towers"][0].split("|")[0], )

        if event == "save_button":
            if not values["new_monkey_name"] or not values["x_pos"] or not values["y_pos"]:
                sg.popup("You didn't fill all of the data!")
                continue

            tower_id = next(id_generator)
            new_tower = Tower(values["new_monkey_name"], int(values["x_pos"]), int(values["y_pos"]))
            towers_list[tower_id] = new_tower
            update_towers_from_list(window["exsiting_towers"], towers_list, additional_tower_information)
            script.append(
                {"action": "create", "name": new_tower.name, "id": tower_id, "x": new_tower.x, "y": new_tower.y})
            update_box_from_script(window["script_box"], script)

        if event == "top_upgrade_button" or event == "middle_upgrade_button" or \
                event == "bottom_upgrade_button" or event == "sell_button" or \
                event == "targeting_button" or event == "s_targeting_button":
            if not values["existing_monkey_name"]:
                sg.popup("You must chose a monkey first!")
                continue

            selected_tower_id = int(values["exsiting_towers"][0].split(":")[0])
            if event == "top_upgrade_button":
                towers_list[selected_tower_id].top += 1  # TODO: overflow
                action = create_upgrade_action(tower_id=selected_tower_id, tier=0)
            elif event == "middle_upgrade_button":
                towers_list[selected_tower_id].middle += 1  # TODO: overflow
                action = create_upgrade_action(tower_id=selected_tower_id, tier=1)
            elif event == "bottom_upgrade_button":
                towers_list[selected_tower_id].bottom += 1  # TODO: overflow
                action = create_upgrade_action(tower_id=selected_tower_id, tier=2)
            elif event == "sell_button":
                # TODO: warn about updating sold towers
                get_additional_information(selected_tower_id, additional_tower_information).sold = True
                action = create_modify_action(tower_id=selected_tower_id, action="sell")
            elif event == "targeting_button":
                # TODO: overflow
                get_additional_information(selected_tower_id, additional_tower_information).targeting += 1
                action = create_modify_action(tower_id=selected_tower_id, action="change_targeting")
            elif event == "s_targeting_button":
                # TODO: overflow
                get_additional_information(selected_tower_id, additional_tower_information).s_targeting += 1
                action = create_modify_action(tower_id=selected_tower_id, action="change_special_targeting")
            else:
                raise RuntimeError

            script.append(action)
            update_towers_from_list(window["exsiting_towers"], towers_list, additional_tower_information)
            update_box_from_script(window["script_box"], script)

        if event == "export_button":
            with open("../exported.json", "w") as of:
                json.dump(script, of)

        if event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    main()
