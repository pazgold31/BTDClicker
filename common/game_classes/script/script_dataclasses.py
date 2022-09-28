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


class PauseEntry(IScriptEntry):
    action = "PauseGame"


class WaitForMoneyEntry(IScriptEntry):
    action = "PauseGame"
    amount: int


class ITowerModifyingScriptEntry(IScriptEntry):
    id: int


class CreateTowerEntry(ITowerModifyingScriptEntry):
    action: str = Actions.create
    name: str
    x: int
    y: int


class UpgradeTowerEntry(ITowerModifyingScriptEntry):
    action: str = Actions.upgrade
    tier: UpgradeTier

    class Config:
        use_enum_values = True


class SellTowerEntry(ITowerModifyingScriptEntry):
    action: str = Actions.sell


class ChangeTargetingEntry(ITowerModifyingScriptEntry):
    action: str = Actions.change_targeting


class ChangeSpecialTargetingEntry(ITowerModifyingScriptEntry):
    action: str = Actions.change_special_targeting


class Script(BaseModel):
    metadata: GameMetadata
    script: List[IScriptEntry]
