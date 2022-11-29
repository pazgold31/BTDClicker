from collections import UserList
from typing import List

from common.game_classes.script.script_entries_dataclasses import IScriptEntry, ITowerModifyingScriptEntry, \
    CreateTowerEntry


class ScriptContainer(UserList[IScriptEntry]):
    def __init__(self, values: List[IScriptEntry] = None):
        values = values or []
        super(ScriptContainer, self).__init__(values)

    def change_position(self, tower_id: int, x: int, y: int):
        for entry in self:
            if isinstance(entry, CreateTowerEntry) and entry.id == tower_id:
                entry.x = x
                entry.y = y

    def change_tower_type(self, tower_id: int, tower_type: str):
        for entry in self:
            if isinstance(entry, CreateTowerEntry) and entry.id == tower_id:
                entry.name = tower_type

    def get_entries_for_id(self, tower_id: int) -> List[ITowerModifyingScriptEntry]:
        output = []
        for entry in self:
            if isinstance(entry, ITowerModifyingScriptEntry) and entry.id == tower_id:
                output.append(entry)

        return output
