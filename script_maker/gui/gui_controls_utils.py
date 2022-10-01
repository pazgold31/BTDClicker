import tkinter
from tkinter.ttk import Combobox
from typing import List, Optional

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.gui.gui_colors import ALTERNATING_LIGHT_COLOR, ALTERNATING_DARK_COLOR
from script_maker.gui.gui_types import ValuesType


class GuiControlsUtils:
    def __init__(self, window: sg.Window):
        self._window = window

    @staticmethod
    def update_listbox(listbox: sg.Listbox, values: Optional[List[str]] = None,
                       set_to_index: Optional[int] = None):
        listbox.update(values=values, set_to_index=set_to_index)

    def are_values_set(self, values: ValuesType, *args: str) -> bool:
        return all(values[i] for i in args)

    def get_selected_index_from_combo(self, key: str) -> int:
        # noinspection PyTypeChecker
        widget: Combobox = self._window[key].widget
        return widget.current()

    def get_selected_value_for_list_box(self, values: ValuesType, key: str) -> str:
        try:
            if len(values[key]) > 1:
                raise ValueError
            return None if not values[key] else values[key][0]
        except KeyError:
            raise ValueError

    def get_selected_indexes_for_list_box(self, key: str) -> List[int]:
        return self._window[key].get_indexes()

    def get_first_selected_index_for_list_box(self, key: str) -> int:
        indexes = self.get_selected_indexes_for_list_box(key=key)
        if len(indexes) > 1:
            raise ValueError

        return None if len(indexes) == 0 else indexes[0]

    def get_last_selected_index_for_list_box(self, key: str) -> int:
        indexes = self.get_selected_indexes_for_list_box(key=key)
        return None if len(indexes) == 0 else indexes[-1]

    def change_cell_color(self, listbox_widget: tkinter.Widget, index: int, color: str):
        listbox_widget: tkinter.Listbox
        listbox_widget.itemconfig(index, bg=color)

    def add_alternating_colors(self, listbox_widget: tkinter.Widget):
        listbox_widget: tkinter.Listbox
        i = 0
        while True:
            try:
                color = ALTERNATING_LIGHT_COLOR if not i % 2 else ALTERNATING_DARK_COLOR
                self.change_cell_color(listbox_widget=listbox_widget, index=i, color=color)
                i += 1
            except tkinter.TclError:
                break
