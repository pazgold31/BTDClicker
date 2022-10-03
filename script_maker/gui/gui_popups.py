from pathlib import Path

# noinspection PyPep8Naming
import PySimpleGUI as sg

from script_maker.script.hotkeys.tower_position_hotkeys import TowerPositionHotkeys


def popup_get_file(message: str, *args, **kwargs) -> Path:
    return Path(sg.popup_get_file(message, *args, **kwargs))


def popup_get_position(title: str, ):
    x_pos_key = "-PopupTowerXpos-"
    y_pos_key = "-PopupTowerYpos-"
    save_button_key = "-PopupTowerSaveButton-"
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
    try:
        with TowerPositionHotkeys(x_pos=window[x_pos_key], y_pos=window[y_pos_key]).capture_positions():
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
