import tkinter
from tkinter.ttk import Combobox
from typing import List

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.gui.gui_colors import ALTERNATING_LIGHT_COLOR, ALTERNATING_DARK_COLOR
from script_maker.gui.gui_types import ValuesType


def are_values_set(values: ValuesType, *args: List[str]) -> bool:
    return all(values[i] for i in args)


def get_selected_index_from_combo(window: sg.Window, key: str) -> int:
    widget: Combobox = window[key].widget
    return widget.current()


def get_selected_value_for_list_box(values: ValuesType, key: str) -> str:
    if len(values[key]) > 1:
        raise ValueError
    return None if not values[key] else values[key][0]


def get_selected_indexes_for_list_box(window: sg.Window, key: str) -> List[int]:
    return window[key].get_indexes()


def get_first_selected_index_for_list_box(window: sg.Window, key: str) -> int:
    indexes = get_selected_indexes_for_list_box(window=window, key=key)
    if len(indexes) > 1:
        raise ValueError

    return None if len(indexes) == 0 else indexes[0]


def get_last_selected_index_for_list_box(window: sg.Window, key: str) -> int:
    indexes = get_selected_indexes_for_list_box(window=window, key=key)
    return None if len(indexes) == 0 else indexes[-1]


def change_cell_color(listbox_widget: tkinter.Widget, index: int, color: str):
    listbox_widget: tkinter.Listbox
    listbox_widget.itemconfig(index, bg=color)


def add_alternating_colors(listbox_widget: tkinter.Widget):
    listbox_widget: tkinter.Listbox
    i = 0
    while True:
        try:
            color = ALTERNATING_LIGHT_COLOR if not i % 2 else ALTERNATING_DARK_COLOR
            change_cell_color(listbox_widget=listbox_widget, index=i, color=color)
            i += 1
        except tkinter.TclError:
            break
