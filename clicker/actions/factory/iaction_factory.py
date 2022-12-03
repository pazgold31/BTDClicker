import abc

from ahk import AHK

from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import IScriptEntry
from script_maker.script.towers_container import TowersContainer


class IActionFactory(metaclass=abc.ABCMeta):
    def create(self, script_entry: IScriptEntry, towers_container: TowersContainer, ahk: AHK, metadata: GameMetadata):
        raise NotImplementedError
