from dataclasses import dataclass
from dataclasses_json import dataclass_json

from common.enums import UpgradeTier

ACTION_KEYWORD = "action"


class Actions:
    create = "create"
    upgrade = "upgrade"
    sell = "sell"
    change_targeting = "change_targeting"
    change_special_targeting = "change_special_targeting"


@dataclass_json
@dataclass
class IAction:
    pass


@dataclass_json
@dataclass
class CreateAction(IAction):
    name: str
    id: int
    x: int
    y: int
    action: str = Actions.create


@dataclass_json
@dataclass
class UpgradeAction(IAction):
    id: int
    tier: UpgradeTier
    action: str = Actions.upgrade


@dataclass_json
@dataclass
class SellAction(IAction):
    id: int
    action: str = Actions.sell


@dataclass_json
@dataclass
class ChangeTargetingAction(IAction):
    id: int
    action: str = Actions.change_targeting


@dataclass_json
@dataclass
class ChangeSpecialTargetingAction(IAction):
    id: int
    action: str = Actions.change_special_targeting
