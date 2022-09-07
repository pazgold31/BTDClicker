from typing import List, Any

import PySimpleGUI as sg

from common.cost.cost_parsing import TOWER_COSTS, HERO_COSTS
from common.enums import Difficulty


class GuiKeys:
    DifficultyListBox = "-difficulty-"
    HeroListBox = "-hero-"
    TowerTypesListBox = "-chosen_tower_type-"
    ExistingTowersListBox = "-existing_towers-"
    XPositionInput = "-xpos-"
    YPositionInput = "-ypos-"
    NewTowerTypeInput = "-new_tower_type_input-"
    SaveTowerButton = '-save_tower_button-'
    KeyboardMouseButton = '-keyboard_mouse_button-'
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
        [sg.Frame("Difficulty",
                  layout=[[sg.Combo(list(DIFFICULTY_MAP.keys()), default_value=list(DIFFICULTY_MAP.keys())[0],
                                    key=GuiKeys.DifficultyListBox, enable_events=True)]]),
         sg.Frame("Hero",
                  layout=[[sg.Combo(get_hero_options(), key=GuiKeys.HeroListBox, enable_events=True)],
                          [sg.Text("(you still need to manually choose the hero before starting the game)")]])],
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
        [sg.Button("Save", enable_events=True, key=GuiKeys.SaveTowerButton),
         sg.Button("Keyboard mouse", enable_events=True, key=GuiKeys.KeyboardMouseButton)],
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


def get_tower_options(difficulty: Difficulty = Difficulty.easy, chosen_hero: str = None) -> List[str]:
    hero_str = "Hero" if not chosen_hero else \
        f"Hero | {chosen_hero}: {HERO_COSTS[chosen_hero].base_cost.get_mapping()[difficulty]}"
    return [hero_str] + \
           [f"{name}: {cost.base_cost.get_mapping()[difficulty]}$" for name, cost in TOWER_COSTS.items()]


def get_hero_options(difficulty: Difficulty = Difficulty.easy) -> List[str]:
    return [f"{name}: {cost.base_cost.get_mapping()[difficulty]}$" for name, cost in HERO_COSTS.items()]
