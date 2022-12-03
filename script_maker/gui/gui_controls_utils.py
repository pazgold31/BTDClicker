import tkinter
from tkinter.ttk import Combobox
from typing import List, Optional, Iterable, Union

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.gui.gui_colors import ALTERNATING_LIGHT_COLOR, ALTERNATING_DARK_COLOR
from script_maker.gui.gui_types import ValuesType


class GuiControlsUtils:
    def __init__(self, window: sg.Window):
        self._window = window

    @staticmethod
    def update_listbox_item(listbox: sg.Listbox, values: Optional[list[str]] = None,
                            set_to_index: Optional[Union[int, Iterable[int]]] = None):
        listbox.update(values=values, set_to_index=set_to_index)

    def update_listbox(self, key: str, values: Optional[list[str]] = None,
                       set_to_index: Optional[Union[int, Iterable[int]]] = None):
        self.update_listbox_item(listbox=self._window[key], values=values, set_to_index=set_to_index)

    @staticmethod
    def update_combo_item(combo: sg.Combo, values: Optional[list[str]] = None, set_to_index: Optional[int] = None):
        combo.update(values=values, set_to_index=set_to_index)

    def update_combo(self, key: str, values: Optional[list[str]] = None, set_to_index: Optional[int] = None):
        self.update_combo_item(combo=self._window[key], values=values, set_to_index=set_to_index)

    @staticmethod
    def update_input_item(input_element: sg.Input, value: Optional[str] = None):
        input_element.update(value=value)

    def update_input(self, key: str, value: Optional[str] = None):
        self.update_input_item(input_element=self._window[key], value=value)

    @staticmethod
    def update_text_item(text_element: sg.Text, value: Optional[str] = None):
        text_element.update(value=value)

    def update_text(self, key: str, value: Optional[str] = None):
        self.update_text_item(text_element=self._window[key], value=value)

    @staticmethod
    def disable_button_item(button: sg.Button):
        button.update(disabled=True)

    def disable_button(self, key: str):
        self.disable_button_item(button=self._window[key])

    @staticmethod
    def are_values_set(values: ValuesType, *args: str) -> bool:
        return all(values[i] for i in args)

    def get_combo_selected_index(self, key: str) -> int:
        # noinspection PyTypeChecker
        widget: Combobox = self._window[key].widget
        return widget.current()

    @staticmethod
    def click_button_item(button: sg.Button):
        button.click()

    def click_button(self, key: str):
        self.click_button_item(button=self._window[key])

    @staticmethod
    def get_selected_value_for_list_box(values: ValuesType, key: str) -> str:
        try:
            if len(values[key]) > 1:
                raise ValueError
            return None if not values[key] else values[key][0]
        except KeyError:
            raise ValueError

    def get_list_box_selected_indexes(self, key: str) -> list[int]:
        return self._window[key].get_indexes()

    def get_list_box_selected_index(self, key: str) -> int:
        indexes = self.get_list_box_selected_indexes(key=key)
        if len(indexes) > 1:
            raise ValueError

        return None if len(indexes) == 0 else indexes[0]

    def get_list_box_last_selected_index(self, key: str) -> int:
        indexes = self.get_list_box_selected_indexes(key=key)
        return None if len(indexes) == 0 else indexes[-1]

    def unselect_listbox(self, key: str):
        self.update_listbox(key=key)

    def change_cell_color(self, key: str, index: int, color: str):
        # noinspection PyTypeChecker
        listbox_widget: tkinter.Listbox = self._window[key].widget
        listbox_widget.itemconfig(index, bg=color)

    def add_alternating_colors(self, key: str):
        for i in range(2 ** 32):
            try:
                color = ALTERNATING_LIGHT_COLOR if not i % 2 else ALTERNATING_DARK_COLOR
                self.change_cell_color(key=key, index=i, color=color)
            except tkinter.TclError:
                break
