from typing import List

from common.game_classes.script.script_dataclasses import IScriptEntry, CreateTowerEntry, ITowerModifyingScriptEntry


class ScriptContainer(List[IScriptEntry]):
    def __init__(self, values: List[IScriptEntry] = None):
        values = values or []
        super(ScriptContainer, self).__init__(values)

    def change_position(self, tower_id: int, x: int, y: int):
        for entry in self:
            if isinstance(entry, CreateTowerEntry) and entry.id == tower_id:
                entry.x = x
                entry.y = y

    def get_entries_for_id(self, tower_id: int) -> List[ITowerModifyingScriptEntry]:
        output = []
        for entry in self:
            if isinstance(entry, ITowerModifyingScriptEntry) and entry.id == tower_id:
                output.append(entry)

        return output
