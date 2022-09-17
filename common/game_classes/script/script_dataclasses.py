from typing import List

from pydantic import BaseModel

from common.game_classes.enums import UpgradeTier, Difficulty

ACTION_KEYWORD = "action"


class Actions:
    create = "create"
    upgrade = "upgrade"
    sell = "sell"
    change_targeting = "change_targeting"
    change_special_targeting = "change_special_targeting"


class GameMetadata(BaseModel):
    difficulty: Difficulty
    hero_type: str

    class Config:
        use_enum_values = True


class IScriptEntry(BaseModel):
    action: str


class CreateTowerEntry(IScriptEntry):
    name: str
    id: int
    x: int
    y: int
    action: str = Actions.create


class UpgradeTowerEntry(IScriptEntry):
    id: int
    tier: UpgradeTier
    action: str = Actions.upgrade

    class Config:
        use_enum_values = True


class SellTowerEntry(IScriptEntry):
    id: int
    action: str = Actions.sell


class ChangeTargetingEntry(IScriptEntry):
    id: int
    action: str = Actions.change_targeting


class ChangeSpecialTargetingEntry(IScriptEntry):
    id: int
    action: str = Actions.change_special_targeting


class Script(BaseModel):
    metadata: GameMetadata
    script: List[IScriptEntry]
