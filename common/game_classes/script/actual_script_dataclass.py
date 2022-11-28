from pydantic import BaseModel

from common.game_classes.script.script_dataclasses import GameMetadata
from script_maker.script.script_container import ScriptContainer


class Script(BaseModel):
    metadata: GameMetadata
    script: ScriptContainer

    class Config:
        arbitrary_types_allowed = True
