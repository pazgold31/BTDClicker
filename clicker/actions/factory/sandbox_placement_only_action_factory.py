from ahk import AHK

from clicker.actions.factory.general_action_factory import GeneralActionFactory
from clicker.actions.factory.iaction_factory import IActionFactory
from clicker.actions.sandbox.SandboxPlaceHeroAction import SandboxPlaceHeroAction
from clicker.actions.sandbox.SandboxPlaceTowerAction import SandboxPlaceTowerAction
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import CreateTowerEntry, \
    CreateHeroEntry
from common.game_classes.script.script_entries_dataclasses import IScriptEntry
from common.game_classes.tower import Tower
from script_maker.script.towers_container import TowersContainer


class SandboxPlacementOnlyActionFactory(IActionFactory):
    def __init__(self):
        self._default_factory = GeneralActionFactory()

    def create(self, script_entry: IScriptEntry, towers_container: TowersContainer, ahk: AHK, metadata: GameMetadata):

        if isinstance(script_entry, CreateTowerEntry):
            return SandboxPlaceTowerAction(ahk=ahk,
                                           tower=towers_container.get_tower_in_type(script_entry.id, Tower),
                                           difficulty=metadata.difficulty)
        elif isinstance(script_entry, CreateHeroEntry):
            return SandboxPlaceHeroAction(ahk=ahk,
                                          hero=towers_container[script_entry.id],
                                          metadata=metadata)
        else:
            return None
