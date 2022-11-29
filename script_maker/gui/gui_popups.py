import threading
from pathlib import Path
from typing import Callable

# noinspection PyPep8Naming
import PySimpleGUI as sg

from common.towers_info.game_info import g_towers_info
from script_maker.gui.gui_controls_utils import GuiControlsUtils
from script_maker.script.hotkeys.tower_position_hotkeys import TowerPositionHotkeys


def popup_get_file(message: str, *args, **kwargs) -> Path:
    try:
        return Path(sg.popup_get_file(message, *args, **kwargs))
    except TypeError:
        raise ValueError


def popup_get_text(message: str, validator: Callable[[str], bool] = None,
                   error_message: str = "", *args, **kwargs) -> str:
    while True:
        text = sg.popup_get_text(message, *args, **kwargs)
        if text is None:
            raise ValueError

        if bool(validator) and not validator(text):
            sg.popup(error_message)
            continue

        break

    return text


def popup_yes_no(*args: str, title: str, **kwargs) -> bool:
    return "Yes" == sg.popup_yes_no(*args, **kwargs, title=title)


def popup_get_position(title: str, ):
    x_pos_key = "-x-"
    y_pos_key = "-y-"
    save_button_key = "-save-"
    layout = [[sg.Text(f"Select position")],
              [sg.Text("Click Ctrl + Shift + R to capture mouse position.")],
              [
                  sg.Text("X"),
                  sg.In(size=(5, 1), enable_events=True, key=x_pos_key),
                  sg.Text("Y"),
                  sg.In(size=(5, 1), enable_events=True, key=y_pos_key)
              ],
              [sg.Button("Save", enable_events=True, key=save_button_key)]]

    window = sg.Window(title, layout, modal=True)
    gui_controls_utils = GuiControlsUtils(window=window)
    try:
        with TowerPositionHotkeys(
                observers=(lambda x, y: gui_controls_utils.update_input(key=x_pos_key, value=x),
                           lambda x, y: gui_controls_utils.update_input(key=y_pos_key, value=y))).capture_positions():
            while True:
                event, values = window.read()
                if event == save_button_key:
                    if not values[x_pos_key] or not values[y_pos_key]:
                        sg.popup("You must specify position")
                        continue

                    return values[x_pos_key], values[y_pos_key]

                if event == "Exit" or event == sg.WIN_CLOSED:
                    raise ValueError("No position selected!")
    finally:
        window.close()


def popup_get_tower_type(title: str, ):
    combo_key = "-combo-"
    save_button_key = "-save-"
    layout = [[sg.Text(f"Select type"),
               sg.Combo(values=list(g_towers_info.keys()), key=combo_key, enable_events=True, readonly=True)],
              [sg.Button("Save", enable_events=True, key=save_button_key)]]

    window = sg.Window(title, layout, modal=True)
    try:
        while True:
            event, values = window.read()
            if event == save_button_key:
                if not values[combo_key]:
                    sg.popup("You must specify type")
                    continue

                return values[combo_key]

            if event == "Exit" or event == sg.WIN_CLOSED:
                raise ValueError("No position selected!")
    finally:
        window.close()


def popup_execute_method(*args, title: str, method: Callable, done_text: str = None, **kwargs):
    ok_key = "-ok-"
    done_text_key = "-done-"
    layout = [[sg.Text(i) for i in args],
              [sg.Text("", key=done_text_key)] if done_text else [],
              [sg.Button("ok", enable_events=True, disabled=True, key=ok_key)]]

    window = sg.Window(title, layout, no_titlebar=True, modal=True, **kwargs)
    t = threading.Thread(target=method)
    t.start()
    try:
        while True:
            event, values = window.read(timeout=200)
            if event == ok_key:
                break

            if not t.is_alive():
                window[ok_key].update(disabled=False)
                if done_text:
                    window[done_text_key].update(value=done_text)

                window.keep_on_top_set()

    finally:
        window.close()
