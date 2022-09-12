from typing import List

import PySimpleGUI as sg

from script_maker.gui.gui_types import ValuesType


def get_value_index_for_list_box(window: sg.Window, values: ValuesType, key: str) -> int:
    return window[key].Values.index(values[key][0])


def are_values_set(values: ValuesType, *args: List[str]) -> bool:
    return all(values[i] for i in args)
