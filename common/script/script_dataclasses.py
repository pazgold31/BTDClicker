from dataclasses import dataclass
from dataclasses_json import dataclass_json

from common.enums import UpgradeTier

ACTION_KEYWORD = "action"


class Actions:
    create = "create"
    upgrade = "upgrade"


@dataclass_json
@dataclass
class CreateAction:
    name: str
    id: int
    x: int
    y: int
    action: str = Actions.create


@dataclass_json
@dataclass
class UpgradeAction:
    id: int
    tier: UpgradeTier
    action: str = Actions.upgrade
