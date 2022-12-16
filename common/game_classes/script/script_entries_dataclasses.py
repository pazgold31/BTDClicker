from pydantic import BaseModel

from common.game_classes.enums import UpgradeTier


class Actions:
    pause = "pause"
    wait_for_money = "wait_for_money"
    remove_obstacle = "remove_obstacle"
    create_tower = "create_tower"
    create_hero = "create_hero"
    upgrade = "upgrade"
    sell = "sell"
    change_targeting = "change_targeting"
    change_special_targeting = "change_special_targeting"


class IScriptEntry(BaseModel):
    action: str


class PauseEntry(IScriptEntry):
    action = Actions.pause


class WaitForMoneyEntry(IScriptEntry):
    action = Actions.wait_for_money
    amount: int


class RemoveObstacleEntry(IScriptEntry):
    action = Actions.remove_obstacle
    x: int
    y: int
    cost: int


class ITowerModifyingScriptEntry(IScriptEntry):
    id: int


class ITowerCreationEntry(ITowerModifyingScriptEntry):
    x: int
    y: int


class CreateTowerEntry(ITowerCreationEntry):
    action: str = Actions.create_tower
    name: str


class CreateHeroEntry(ITowerCreationEntry):
    action: str = Actions.create_hero


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
