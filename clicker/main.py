import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

from ahk import AHK

from actions.PlaceTowerAction import PlaceTowerAction
from actions.UpgradeTowerAction import UpgradeTowerAction
from clicker.actions.ChangeSpecialTargetingAction import ChangeSpecialTargetingAction
from clicker.actions.ChangeTargetingAction import ChangeTargetingAction
from clicker.actions.IAction import IAction
from clicker.actions.SellTowerAction import SellTowerAction
from common.enums import Difficulty, UpgradeTier
from common.script.script_dataclasses import CreateTowerEntry, ACTION_KEYWORD, Actions, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry
from common.tower import Tower


def load_script_dict(file_path: Path = Path("../exported.json")) -> Dict:
    with file_path.open("r") as of:
        return json.load(of)


def create_script(ahk: AHK, script_dict: Dict) -> Tuple[List[IAction], Dict[int, Tower]]:
    script = []
    tower_map: Dict[int, Tower] = {}
    for action in script_dict:
        if action[ACTION_KEYWORD] == Actions.create:
            action_class: CreateTowerEntry = CreateTowerEntry.from_dict(action)
            tower = Tower(name=action_class.name, x=action_class.x, y=action_class.y)
            tower_map[action_class.id] = tower
            script.append(PlaceTowerAction(ahk=ahk, tower=tower, difficulty=Difficulty.easy))
        elif action[ACTION_KEYWORD] == Actions.upgrade:
            action_class: UpgradeTowerEntry = UpgradeTowerEntry.from_dict(action)
            script.append(UpgradeTowerAction(ahk=ahk, tower=tower_map[action_class.id],
                                             tier=UpgradeTier(action_class.tier),
                                             difficulty=Difficulty.easy))
        elif action[ACTION_KEYWORD] == Actions.sell:
            action_class: SellTowerEntry = SellTowerEntry.from_dict(action)
            script.append(SellTowerAction(ahk=ahk, tower=tower_map[action_class.id]))
        elif action[ACTION_KEYWORD] == Actions.change_targeting:
            action_class: ChangeTargetingEntry = ChangeTargetingEntry.from_dict(action)
            script.append(ChangeTargetingAction(ahk=ahk, tower=tower_map[action_class.id]))
        elif action[ACTION_KEYWORD] == Actions.change_special_targeting:
            action_class: ChangeSpecialTargetingEntry = ChangeSpecialTargetingEntry.from_dict(action)
            script.append(ChangeSpecialTargetingAction(ahk=ahk, tower=tower_map[action_class.id]))

    return script, tower_map


def main():
    ahk = AHK()
    total_dict = load_script_dict()
    metadata = total_dict["metadata"]
    script_dict = total_dict["script"]
    script, tower_map = create_script(ahk=ahk, script_dict=script_dict)
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
