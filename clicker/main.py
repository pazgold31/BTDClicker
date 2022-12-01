import json
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List, Tuple

from ahk import AHK

from actions.PlaceTowerAction import PlaceTowerAction
from actions.UpgradeTowerAction import UpgradeTowerAction
from clicker.actions.ChangeSpecialTargetingAction import ChangeSpecialTargetingAction
from clicker.actions.ChangeTargetingAction import ChangeTargetingAction
from clicker.actions.IAction import IAction
from clicker.actions.PauseGameAction import PauseGameAction
from clicker.actions.PlaceHeroAction import PlaceHeroAction
from clicker.actions.SellTowerAction import SellTowerAction
from clicker.actions.WaitForMoneyAction import WaitForMoneyAction
from clicker.clicker_state import g_clicker_state
from clicker.consts.timing_consts import ACTIONS_DELAY, ACTION_CHECKING_DELAY, CLICKER_START_DELAY, \
    KEYBOARD_LAYOUT_DELAY
from common.game_classes.enums import UpgradeTier
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import PauseEntry, WaitForMoneyEntry, CreateTowerEntry, \
    UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry, CreateHeroEntry
from common.game_classes.script.script_parsing import import_script, parse_towers_from_script, parse_metadata
from common.game_classes.tower import Tower
from common.hotkeys import Hotkeys
from common.keyboard import is_language_valid
from script_maker.script.towers_container import TowersContainer


def load_script_dict(file_path: Path) -> Dict:
    with file_path.open("r") as of:
        return json.load(of)


def get_script_path() -> Path:
    return Path(input("Enter script path: "))


def remove_towers_upgrades(towers_container: TowersContainer):
    for t in towers_container.values():
        if not isinstance(t, Tower):
            continue

        t.tier_map[UpgradeTier.top] = 0
        t.tier_map[UpgradeTier.middle] = 0
        t.tier_map[UpgradeTier.bottom] = 0


def create_script(ahk: AHK, script_dict: Dict, metadata: GameMetadata) -> Tuple[List[IAction], TowersContainer]:
    script_entries = import_script(script_dict=script_dict)
    towers_container: TowersContainer = parse_towers_from_script(script_entries=script_entries)
    remove_towers_upgrades(towers_container=towers_container)

    def get_tower_from_map(tower_id: int) -> Tower:
        tower = towers_container[tower_id]
        if not isinstance(tower, Tower):
            raise RuntimeError

        return tower

    script: List[IAction] = []
    for script_entry in script_entries:
        if isinstance(script_entry, PauseEntry):
            script.append(PauseGameAction(ahk=ahk))
        if isinstance(script_entry, WaitForMoneyEntry):
            script.append(WaitForMoneyAction(ahk=ahk, amount=script_entry.amount))
        if isinstance(script_entry, CreateTowerEntry):
            script.append(PlaceTowerAction(ahk=ahk, tower=towers_container[script_entry.id],
                                           difficulty=metadata.difficulty))
        elif isinstance(script_entry, CreateHeroEntry):
            script.append(PlaceHeroAction(ahk=ahk, hero=towers_container[script_entry.id], metadata=metadata))
        elif isinstance(script_entry, UpgradeTowerEntry):
            script.append(UpgradeTowerAction(ahk=ahk, tower=get_tower_from_map(script_entry.id),
                                             tier=UpgradeTier(script_entry.tier),
                                             difficulty=metadata.difficulty))
        elif isinstance(script_entry, SellTowerEntry):
            script.append(SellTowerAction(ahk=ahk, tower=get_tower_from_map(script_entry.id)))
        elif isinstance(script_entry, ChangeTargetingEntry):
            script.append(ChangeTargetingAction(ahk=ahk, tower=get_tower_from_map(script_entry.id)))
        elif isinstance(script_entry, ChangeSpecialTargetingEntry):
            script.append(ChangeSpecialTargetingAction(ahk=ahk, tower=get_tower_from_map(script_entry.id)))

    return script, towers_container


def parse_args() -> Namespace:
    argument_parser = ArgumentParser("BTD6 script player")
    argument_parser.add_argument("-s", "--script", type=Path, required=False, default=None)
    return argument_parser.parse_args()


def main():
    args = parse_args()

    if not is_language_valid():
        raise RuntimeError("Invalid keyboard language selected. Please change it and execute again.")

    total_dict = load_script_dict(file_path=args.script or get_script_path())
    metadata = parse_metadata(json_dict=total_dict)

    ahk = AHK()
    Hotkeys.add_hotkey("ctrl + shift + s", g_clicker_state.stop)
    Hotkeys.add_hotkey("ctrl + shift + c", g_clicker_state.run)

    script, tower_map = create_script(ahk=ahk, script_dict=total_dict["script"], metadata=metadata)

    time.sleep(CLICKER_START_DELAY)

    for action in script:
        print(f"Next: {action.get_action_message()}")
        while True:
            if not is_language_valid():
                print("Invalid keyboard layout, please change it.")
                time.sleep(KEYBOARD_LAYOUT_DELAY)
                continue

            if not g_clicker_state.is_stopped() and action.can_act():
                action.act()
                break

            time.sleep(ACTION_CHECKING_DELAY)

        time.sleep(ACTIONS_DELAY)


if __name__ == '__main__':
    main()
    print("Done")
