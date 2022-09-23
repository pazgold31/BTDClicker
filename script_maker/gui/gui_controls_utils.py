from typing import List

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.gui.gui_types import ValuesType


def are_values_set(values: ValuesType, *args: List[str]) -> bool:
    return all(values[i] for i in args)


def get_selected_index_for_list_box(window: sg.Window, key: str) -> int:
    indexes = window[key].get_indexes()
    if len(indexes) > 1:
        raise ValueError

    return None if len(indexes) == 0 else indexes[0]
