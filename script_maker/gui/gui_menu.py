from script_maker.hotkey_map import format_to_text, ScriptHotkeyMap


class GuiMenu:
    class File:
        MenuName = "File"
        New = f"New    {format_to_text(ScriptHotkeyMap.new_script)}"
        Import = f"Import    {format_to_text(ScriptHotkeyMap.import_script)}"
        Save = f"Save    {format_to_text(ScriptHotkeyMap.save_script)}"
        SaveAs = f"Save as    {format_to_text(ScriptHotkeyMap.save_script_as)}"

    class ViewedTowers:
        MenuName = "Viewed Towers"
        All = f"All    {format_to_text(ScriptHotkeyMap.view_all_towers)}"
        Primary = f"Primary    {format_to_text(ScriptHotkeyMap.view_primary_towers)}"
        Military = f"Military    {format_to_text(ScriptHotkeyMap.view_military_towers)}"
        Magic = f"Magic    {format_to_text(ScriptHotkeyMap.view_magic_towers)}"
        Support = f"Support    {format_to_text(ScriptHotkeyMap.view_support_towers)}"
