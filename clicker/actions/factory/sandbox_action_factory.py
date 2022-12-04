from ahk import AHK

from clicker.actions.factory.general_action_factory import GeneralActionFactory
from clicker.actions.factory.iaction_factory import IActionFactory
from clicker.actions.sandbox.SandboxPlaceHeroAction import SandboxPlaceHeroAction
from clicker.actions.sandbox.SandboxPlaceTowerAction import SandboxPlaceTowerAction
from clicker.actions.sandbox.SandboxUpgradeTowerAction import SandboxUpgradeTowerAction
from common.game_classes.enums import UpgradeTier
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import CreateTowerEntry, \
    UpgradeTowerEntry, CreateHeroEntry
from common.game_classes.script.script_entries_dataclasses import IScriptEntry
from common.game_classes.tower import Tower
from script_maker.script.towers_container import TowersContainer


class SandboxGeneralActionFactory(IActionFactory):
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
        elif isinstance(script_entry, UpgradeTowerEntry):
            return SandboxUpgradeTowerAction(ahk=ahk,
                                             tower=towers_container.get_tower_in_type(script_entry.id, Tower),
                                             tier=UpgradeTier(script_entry.tier),
                                             difficulty=metadata.difficulty)
        else:
            self._default_factory.create(script_entry=script_entry, towers_container=towers_container,
                                         ahk=ahk, metadata=metadata)
