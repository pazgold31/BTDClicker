import re
from typing import Iterable

from pydantic import BaseModel

from clicker.consts.keymap import Keymap


def run_subs_on_text(text: str, replacements: Iterable[Iterable[str]]) -> str:
    for pattern, new_pattern in replacements:
        text = re.sub(pattern, new_pattern, text)

    return text


def format_to_text(hotkey: str) -> str:
    replacements = ((r"<Control_L>([\d\w]+)", r"ctrl + \g<1>"),
                    (r"<Control-([\d\w]+)>", r"ctrl + \g<1>"),
                    (r"<Control-Shift-([\d\w]+)>", r"ctrl + shift + \g<1>"))
    return run_subs_on_text(text=hotkey, replacements=replacements)


def convert_ahk_to_tkinter(hotkey: str) -> str:
    replacements = ((r"{(.*)}", r"<\g<1>>"),)
    return run_subs_on_text(text=hotkey, replacements=replacements)


class ScriptMakerHotkeys(BaseModel):
    # Global system hotkeys.
    capture_tower_position: str = "ctrl + shift + r"
    save_tower: str = "ctrl + shift + s"
    duplicate_tower: str = "ctrl + shift + d"
    modify_tower_position: str = "ctrl + shift + p"

    # Window specific hotkeys
    new_script: str = "<Control-n>"
    import_script: str = "<Control-o>"
    save_script: str = "<Control-s>"
    save_script_as: str = "<Control-Shift-S>"

    view_all_towers: str = "<Control_L>1"
    view_primary_towers: str = "<Control_L>2"
    view_military_towers: str = "<Control_L>3"
    view_magic_towers: str = "<Control_L>4"
    view_support_towers: str = "<Control_L>5"

    copy_towers_to_clipboard: str = "<Control-c>"
    paste_towers_from_clipboard: str = "<Control-v>"
    double_click: str = "<Double-Button-1>"

    save_upgraded: str = "<Control-Alt-s>"
    keyboard_mouse: str = "<Control-k>"
    upgrade_top: str = f"{Keymap.upgrade_top}"
    upgrade_middle: str = f"{Keymap.upgrade_middle}"
    upgrade_bottom: str = f"{Keymap.upgrade_bottom}"
    sell: str = convert_ahk_to_tkinter(Keymap.sell)
    change_targeting: str = ""
    change_special_targeting: str = ""
    delete_tower: str = "<Control-Delete>"
    modify_tower_type: str = "<Control-t>"
    pause_game: str = "<Control-p>"
    delete_script: str = "<Control-Shift-Delete>"
    delete_up_script: str = "<Control-Shift-Prior>"
    move_down_script: str = "<Control-Shift-Next>"


ScriptHotkeyMap = ScriptMakerHotkeys()
