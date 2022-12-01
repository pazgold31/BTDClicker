from typing import Dict, List, Generator, Tuple

from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import Actions, IScriptEntry, PauseEntry, \
    WaitForMoneyEntry, CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, \
    ChangeSpecialTargetingEntry
from common.game_classes.tower import Tower, Hero
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer

ACTION_KEYWORD = "action"


def import_script(script_dict: Dict) -> ScriptContainer:
    script: List[IScriptEntry] = []

    for action in script_dict:
        if action[ACTION_KEYWORD] == Actions.pause:
            script.append(PauseEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.wait_for_money:
            script.append(WaitForMoneyEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.create:
            script.append(CreateTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.upgrade:
            script.append(UpgradeTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.sell:
            script.append(SellTowerEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.change_targeting:
            script.append(ChangeTargetingEntry.parse_obj(action))
        elif action[ACTION_KEYWORD] == Actions.change_special_targeting:
            script.append(ChangeSpecialTargetingEntry.parse_obj(action))

    return ScriptContainer(script)


def dynamic_script_parsing(script_entries: ScriptContainer,
                           metadata: GameMetadata) -> Generator[Tuple[TowersContainer, IScriptEntry], None, None]:
    # TODO: remove the metadata since heroes don't need names
    towers_container = TowersContainer()
    for script_entry in script_entries:
        if isinstance(script_entry, CreateTowerEntry):
            if "Hero" == script_entry.name:
                tower = Hero(name=metadata.hero_type, x=script_entry.x, y=script_entry.y)
            else:
                tower = Tower(name=script_entry.name, x=script_entry.x, y=script_entry.y)
            towers_container[script_entry.id] = tower

        elif isinstance(script_entry, UpgradeTowerEntry):
            tower_obj = towers_container[script_entry.id]
            if not isinstance(tower_obj, Tower):
                raise RuntimeError

            tower_obj.tier_map[script_entry.tier] += 1

        elif isinstance(script_entry, SellTowerEntry):
            towers_container[script_entry.id].sold = True
        elif isinstance(script_entry, ChangeTargetingEntry):
            towers_container[script_entry.id].targeting += 1
        elif isinstance(script_entry, ChangeSpecialTargetingEntry):
            towers_container[script_entry.id].s_targeting += 1

        yield towers_container, script_entry


def parse_towers_from_script(script_entries: ScriptContainer, metadata: GameMetadata) -> TowersContainer:
    *_, last_output = dynamic_script_parsing(script_entries=script_entries, metadata=metadata)
    return last_output[0]  # Towers container


def parse_metadata(json_dict: Dict) -> GameMetadata:
    return GameMetadata.parse_obj(json_dict["metadata"])
