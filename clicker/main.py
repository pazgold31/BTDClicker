import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Type

from ahk import AHK
from pydantic import parse_raw_as

from actions.PlaceTowerAction import PlaceTowerAction
from actions.UpgradeTowerAction import UpgradeTowerAction
from clicker.actions.ChangeSpecialTargetingAction import ChangeSpecialTargetingAction
from clicker.actions.ChangeTargetingAction import ChangeTargetingAction
from clicker.actions.IAction import IAction
from clicker.actions.PlaceHeroAction import PlaceHeroAction
from clicker.actions.SellTowerAction import SellTowerAction
from common.enums import Difficulty, UpgradeTier
from common.keyboard import is_language_valid
from common.script.script_dataclasses import CreateTowerEntry, ACTION_KEYWORD, Actions, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry, GameMetadata
from common.tower import Tower, Hero


def load_script_dict(file_path: Path = Path("../exported.json")) -> Dict:
    with file_path.open("r") as of:
        return json.load(of)


def create_script(ahk: AHK, script_dict: Dict, metadata: GameMetadata) -> Tuple[List[IAction], Dict[int, Tower]]:
    script = []
    tower_map: Dict[int, Tower] = {}
    for action in script_dict:
        if action[ACTION_KEYWORD] == Actions.create:
            action_class: CreateTowerEntry = CreateTowerEntry.parse_obj(action)
            if "Hero" == action_class.name:
                tower = Hero(name=metadata.hero_type, x=action_class.x, y=action_class.y)
                created_action = PlaceHeroAction(ahk=ahk, hero=tower, difficulty=metadata.difficulty)
            else:
                tower = Tower(name=action_class.name, x=action_class.x, y=action_class.y)
                created_action = PlaceTowerAction(ahk=ahk, tower=tower, difficulty=metadata.difficulty)

            tower_map[action_class.id] = tower
            script.append(created_action)
        elif action[ACTION_KEYWORD] == Actions.upgrade:
            action_class: UpgradeTowerEntry = UpgradeTowerEntry.parse_obj(action)
            script.append(UpgradeTowerAction(ahk=ahk, tower=tower_map[action_class.id],
                                             tier=UpgradeTier(action_class.tier),
                                             difficulty=metadata.difficulty))
        elif action[ACTION_KEYWORD] == Actions.sell:
            action_class: SellTowerEntry = SellTowerEntry.parse_obj(action)
            script.append(SellTowerAction(ahk=ahk, tower=tower_map[action_class.id]))
        elif action[ACTION_KEYWORD] == Actions.change_targeting:
            action_class: ChangeTargetingEntry = ChangeTargetingEntry.parse_obj(action)
            script.append(ChangeTargetingAction(ahk=ahk, tower=tower_map[action_class.id]))
        elif action[ACTION_KEYWORD] == Actions.change_special_targeting:
            action_class: ChangeSpecialTargetingEntry = ChangeSpecialTargetingEntry.parse_obj(action)
            script.append(ChangeSpecialTargetingAction(ahk=ahk, tower=tower_map[action_class.id]))

    return script, tower_map


def main():
    if not is_language_valid():
        raise RuntimeError("Invalid keyboard language selected. Please change it and execute again.")
    ahk = AHK()
    total_dict = load_script_dict()
    metadata = GameMetadata.parse_obj(total_dict["metadata"])
    script, tower_map = create_script(ahk=ahk, script_dict=total_dict["script"], metadata=metadata)
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
