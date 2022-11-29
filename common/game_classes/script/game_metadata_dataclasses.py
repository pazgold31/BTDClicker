from pydantic import BaseModel

from common.game_classes.enums import Difficulty


class GameMetadata(BaseModel):
    difficulty: Difficulty
    hero_type: str

    class Config:
        use_enum_values = True


