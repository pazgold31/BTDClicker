from typing import Dict, List

from common.script.script_dataclasses import ACTION_KEYWORD, Actions, CreateTowerEntry, UpgradeTowerEntry, \
    ChangeTargetingEntry, ChangeSpecialTargetingEntry, SellTowerEntry, IScriptEntry, GameMetadata
from common.tower import Tower, Hero, BaseTower


def import_script(script_dict: Dict) -> List[IScriptEntry]:
    script: List[IScriptEntry] = []

    for action in script_dict:
        if action[ACTION_KEYWORD] == Actions.create:
            script.append(CreateTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.upgrade:
            script.append(UpgradeTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.sell:
            script.append(SellTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.change_targeting:
            script.append(ChangeTargetingEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.change_special_targeting:
            script.append(ChangeSpecialTargetingEntry.parse_obj(action))

    return script


def parse_towers_from_script(script_entries: List[IScriptEntry], metadata: GameMetadata):
    tower_map: Dict[int, BaseTower] = {}
    for script_entry in script_entries:
        if isinstance(script_entry, CreateTowerEntry):
            if "Hero" == script_entry.name:
                tower = Hero(name=metadata.hero_type, x=script_entry.x, y=script_entry.y)
            else:
                tower = Tower(name=script_entry.name, x=script_entry.x, y=script_entry.y)

            tower_map[script_entry.id] = tower
    return tower_map


def parse_metadata(json_dict: Dict) -> GameMetadata:
    return GameMetadata.parse_obj(json_dict["metadata"])
