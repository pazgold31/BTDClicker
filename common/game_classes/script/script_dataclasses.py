from collections import UserList

from pydantic import BaseModel

from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import IScriptEntry


class Script(BaseModel):
    metadata: GameMetadata
    script: UserList[IScriptEntry]

    class Config:
        arbitrary_types_allowed = True
