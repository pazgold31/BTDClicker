import tkinter
from typing import List

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.gui.gui_colors import ALTERNATING_LIGHT_COLOR, ALTERNATING_DARK_COLOR
from script_maker.gui.gui_types import ValuesType


def are_values_set(values: ValuesType, *args: List[str]) -> bool:
    return all(values[i] for i in args)


def get_selected_index_for_list_box(window: sg.Window, key: str) -> int:
    indexes = window[key].get_indexes()
    if len(indexes) > 1:
        raise ValueError

    return None if len(indexes) == 0 else indexes[0]


def change_cell_color(listbox_widget: tkinter.Listbox, index: int, color: str):
    listbox_widget.itemconfig(index, bg=color)


def add_alternating_colors(listbox_widget: tkinter.Listbox):
    i = 0
    while True:
        try:
            color = ALTERNATING_LIGHT_COLOR if not i % 2 else ALTERNATING_DARK_COLOR
            change_cell_color(listbox_widget=listbox_widget, index=i, color=color)
            i += 1
        except tkinter.TclError:
            break
