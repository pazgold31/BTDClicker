import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

from ahk import AHK

from actions.PlaceTowerAction import PlaceTowerAction
from actions.UpgradeTowerAction import UpgradeTowerAction
from clicker.actions.IAction import IAction
from common.enums import Difficulty, UpgradeTier
from common.script.script_dataclasses import CreateAction, ACTION_KEYWORD, Actions, UpgradeAction
from common.tower import Tower


def load_script_dict(file_path: Path = Path("../exported.json")) -> Dict:
    with file_path.open("r") as of:
        return json.load(of)


def create_script(ahk: AHK, script_dict: Dict) -> Tuple[List[IAction], Dict[int, Tower]]:
    script = []
    tower_map: Dict[int, Tower] = {}
    for action in script_dict:
        if action[ACTION_KEYWORD] == Actions.create:
            create_action: CreateAction = CreateAction.from_dict(action)
            tower = Tower(name=create_action.name, x=create_action.x, y=create_action.y)
            tower_map[create_action.id] = tower
            script.append(PlaceTowerAction(ahk=ahk, tower=tower, difficulty=Difficulty.easy))
        elif action[ACTION_KEYWORD] == Actions.upgrade:
            upgrade_action: UpgradeAction = UpgradeAction.from_dict(action)
            script.append(UpgradeTowerAction(ahk=ahk, tower=tower_map[upgrade_action.id],
                                             tier=UpgradeTier(upgrade_action.tier),
                                             difficulty=Difficulty.easy))

    return script, tower_map


def main():
    ahk = AHK()
    script, tower_map = create_script(ahk=ahk, script_dict=load_script_dict())
    time.sleep(2)

    for action in script:
        while True:
            if action.can_act():
                action.act()
                break

            time.sleep(0.5)


if __name__ == '__main__':
    main()
    print("Done")
