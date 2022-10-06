import re

from pydantic import BaseModel


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


def format_to_text(hotkey: str) -> str:
    replacements = ((r"<Control_L>([\d\w]+)", r"ctrl + \g<1>"),
                    (r"<Control-([\d\w]+)>", r"ctrl + \g<1>"),
                    (r"<Control-Shift-([\d\w]+)>", r"ctrl + shift + \g<1>"))
    for pattern, new_pattern in replacements:
        hotkey = re.sub(pattern, new_pattern, hotkey)

    return hotkey


ScriptHotkeyMap = ScriptMakerHotkeys()
