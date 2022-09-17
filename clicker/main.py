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
from common.enums import UpgradeTier
from common.keyboard import is_language_valid
from common.script.script_dataclasses import CreateTowerEntry, ACTION_KEYWORD, Actions, UpgradeTowerEntry, \
    SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry, GameMetadata
from common.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.tower import Tower, Hero, BaseTower


def load_script_dict(file_path: Path = Path("../exported.json")) -> Dict:
    with file_path.open("r") as of:
        return json.load(of)


def create_script(ahk: AHK, script_dict: Dict, metadata: GameMetadata) -> Tuple[List[IAction], Dict[int, BaseTower]]:
    script_entries = import_script(script_dict=script_dict)
    tower_map: Dict[int, BaseTower] = parse_towers_from_script(script_entries=script_entries, metadata=metadata)
    script: List[IAction] = []
    for script_entry in script_entries:
        if isinstance(script_entry, CreateTowerEntry):
            if "Hero" == script_entry.name:
                script.append(PlaceHeroAction(ahk=ahk, hero=tower_map[script_entry.id],
                                              difficulty=metadata.difficulty))
            else:
                script.append(PlaceTowerAction(ahk=ahk, tower=tower_map[script_entry.id],
                                               difficulty=metadata.difficulty))

        elif isinstance(script_entry, UpgradeTowerEntry):
            script.append(UpgradeTowerAction(ahk=ahk, tower=tower_map[script_entry.id],
                                             tier=UpgradeTier(script_entry.tier),
                                             difficulty=metadata.difficulty))
        elif isinstance(script_entry, SellTowerEntry):
            script.append(SellTowerAction(ahk=ahk, tower=tower_map[script_entry.id]))
        elif isinstance(script_entry, ChangeTargetingEntry):
            script.append(ChangeTargetingAction(ahk=ahk, tower=tower_map[script_entry.id]))
        elif isinstance(script_entry, ChangeSpecialTargetingEntry):
            script.append(ChangeSpecialTargetingAction(ahk=ahk, tower=tower_map[script_entry.id]))

    return script, tower_map


def main():
    if not is_language_valid():
        raise RuntimeError("Invalid keyboard language selected. Please change it and execute again.")
    ahk = AHK()
    total_dict = load_script_dict()
    metadata = parse_metadata(json_dict=total_dict)
    script, tower_map = create_script(ahk=ahk, script_dict=total_dict["script"], metadata=metadata)
    time.sleep(2)

    for action in script:
        print(f"Next: {action.get_action_message()}")
        while True:
            if action.can_act():
                action.act()
                break

            time.sleep(0.2)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
    print("Done")
