from typing import List, Any

# noinspection PyPep8Naming
import PySimpleGUI as sg

from common.game_classes.enums import Difficulty
from script_maker.gui.gui_formatters import GuiFormatters
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_menu import GuiMenu

DIFFICULTY_MAP = {"easy": Difficulty.easy, "medium": Difficulty.medium,
                  "hard": Difficulty.hard, "impopable": Difficulty.impopable}


def get_layout() -> List[List[Any]]:
    menu = [[GuiMenu.File.MenuName, [GuiMenu.File.New, GuiMenu.File.Import, GuiMenu.File.Save, GuiMenu.File.SaveAs]],
            [GuiMenu.ViewedTowers.MenuName,
             [GuiMenu.ViewedTowers.All, GuiMenu.ViewedTowers.Primary, GuiMenu.ViewedTowers.Military,
              GuiMenu.ViewedTowers.Magic, GuiMenu.ViewedTowers.Support]]]

    left_col = [
        [sg.Frame("Difficulty",
                  layout=[[sg.Combo(values=list(DIFFICULTY_MAP.keys()), default_value=list(DIFFICULTY_MAP.keys())[0],
                                    key=GuiKeys.DifficultyListBox, enable_events=True, readonly=True)]]),
         sg.Frame("Hero",
                  layout=[[sg.Combo(values=GuiFormatters.format_hero_options(),
                                    default_value=GuiFormatters.format_hero_options()[0],
                                    key=GuiKeys.HeroCombo, enable_events=True, readonly=True)],
                          [sg.Text("(you still need to manually choose the hero before starting the game)")]])],
        [sg.Text("Towers", size=(30, 1), font="Lucida", justification="left")],
        [sg.Listbox(values=[],
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
        [sg.Button("Modify Position", size=(15, 1), enable_events=True, key=GuiKeys.ModifyTowerPositionButton),
         sg.Button("Duplicate Tower", size=(15, 1), enable_events=True, key=GuiKeys.DuplicateTowerButton),
         sg.Button("Delete Tower", size=(15, 1), enable_events=True, key=GuiKeys.DeleteTowerButton)],
        [sg.Button("Modify Type", size=(15, 1), enable_events=True, key=GuiKeys.ModifyTowerTypeButton)],
        [sg.HSeparator()],
        [sg.Button("Pause game", size=(15, 1), enable_events=True, key=GuiKeys.PauseGameButton),
         sg.Frame("", layout=[[sg.In(size=(12, 1), enable_events=True, key=GuiKeys.WaitForMoneyInput),
                               sg.Button("Wait for amount", size=(15, 1), enable_events=True,
                                         key=GuiKeys.WaitForMoneyButton)]])],
        [sg.HSeparator()],
        [sg.Text("Total cost: ", key=GuiKeys.TotalCostText)]
    ]

    bottom_left_col = [[sg.Text("Script:")],
                       [sg.Listbox(values=[], select_mode="extended", key=GuiKeys.ScriptBox, size=(150, 12),
                                   enable_events=True)]]

    bottom_right_col = [[sg.Button("Delete", size=(15, 1), enable_events=True, key=GuiKeys.DeleteFromScriptButton)],
                        [sg.Button("Move Up", size=(15, 1), enable_events=True, key=GuiKeys.MoveUpInScriptButton)],
                        [sg.Button("Move Down", size=(15, 1), enable_events=True, key=GuiKeys.MoveDownInScriptButton)]]

    bottom_layout = [[sg.Column(bottom_left_col), sg.VSeparator(), sg.Column(bottom_right_col)]]

    return [[sg.Menu(menu, tearoff=False, pad=(200, 1), key=GuiKeys.MenuKey)],
            [sg.Column(left_col),
             sg.VSeparator(),
             sg.Column(right_col)],
            bottom_layout]
