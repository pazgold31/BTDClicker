import json
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, Tuple

from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.actions.factory.general_action_factory import GeneralActionFactory
from clicker.clicker_state import g_clicker_state
from clicker.consts.timing_consts import ACTIONS_DELAY, ACTION_CHECKING_DELAY, CLICKER_START_DELAY, \
    KEYBOARD_LAYOUT_DELAY
from common.game_classes.enums import UpgradeTier
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_parsing import parse_towers_from_script, parse_metadata, import_script
from common.game_classes.tower import Tower
from common.hotkeys import Hotkeys
from common.keyboard import is_language_valid
from script_maker.script.script_container import ScriptContainer
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


def get_towers_from_script(script_entries: ScriptContainer) -> TowersContainer:
    towers_container: TowersContainer = parse_towers_from_script(script_entries=script_entries)
    remove_towers_upgrades(towers_container=towers_container)
    return towers_container


def create_script(ahk: AHK, script_entries: ScriptContainer,
                  towers_container: TowersContainer, metadata: GameMetadata) -> Tuple[list[IAction], TowersContainer]:
    actions_factory = GeneralActionFactory()

    return [actions_factory.create(script_entry=i, towers_container=towers_container,
                                   ahk=ahk, metadata=metadata) for i in script_entries], towers_container


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

    script_entries = import_script(script_dict=total_dict["script"])

    towers_container = get_towers_from_script(script_entries=script_entries)
    script, tower_map = create_script(ahk=ahk, script_entries=script_entries,
                                      towers_container=towers_container, metadata=metadata)

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
