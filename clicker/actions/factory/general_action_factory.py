from ahk import AHK

from clicker.actions.factory.iaction_factory import IActionFactory
from clicker.actions.general.ChangeSpecialTargetingAction import ChangeSpecialTargetingAction
from clicker.actions.general.ChangeTargetingAction import ChangeTargetingAction
from clicker.actions.general.PauseGameAction import PauseGameAction
from clicker.actions.general.PlaceHeroAction import PlaceHeroAction
from clicker.actions.general.PlaceTowerAction import PlaceTowerAction
from clicker.actions.general.SellTowerAction import SellTowerAction
from clicker.actions.general.UpgradeTowerAction import UpgradeTowerAction
from clicker.actions.general.WaitForMoneyAction import WaitForMoneyAction
from common.game_classes.enums import UpgradeTier
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.script.script_entries_dataclasses import IScriptEntry, PauseEntry
from common.game_classes.script.script_entries_dataclasses import WaitForMoneyEntry, CreateTowerEntry, \
    UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, ChangeSpecialTargetingEntry, CreateHeroEntry
from common.game_classes.tower import Tower
from script_maker.script.towers_container import TowersContainer


class GeneralActionFactory(IActionFactory):
    def __init__(self):
        pass

    def create(self, script_entry: IScriptEntry, towers_container: TowersContainer, ahk: AHK, metadata: GameMetadata):
        if isinstance(script_entry, PauseEntry):
            return PauseGameAction(ahk=ahk)
        elif isinstance(script_entry, WaitForMoneyEntry):
            return WaitForMoneyAction(ahk=ahk, amount=script_entry.amount)

        elif isinstance(script_entry, CreateTowerEntry):
            return PlaceTowerAction(ahk=ahk,
                                    tower=towers_container.get_tower_in_type(script_entry.id, Tower),
                                    difficulty=metadata.difficulty)
        elif isinstance(script_entry, CreateHeroEntry):
            return PlaceHeroAction(ahk=ahk,
                                   hero=towers_container[script_entry.id],
                                   metadata=metadata)
        elif isinstance(script_entry, UpgradeTowerEntry):
            return UpgradeTowerAction(ahk=ahk,
                                      tower=towers_container.get_tower_in_type(script_entry.id, Tower),
                                      tier=UpgradeTier(script_entry.tier),
                                      difficulty=metadata.difficulty)
        elif isinstance(script_entry, SellTowerEntry):
            return SellTowerAction(ahk=ahk,
                                   tower=towers_container.get_tower_in_type(script_entry.id, Tower))
        elif isinstance(script_entry, ChangeTargetingEntry):
            return ChangeTargetingAction(ahk=ahk,
                                         tower=towers_container.get_tower_in_type(script_entry.id, Tower))
        elif isinstance(script_entry, ChangeSpecialTargetingEntry):
            return ChangeSpecialTargetingAction(ahk=ahk,
                                                tower=towers_container.get_tower_in_type(script_entry.id, Tower))
        else:
            raise RuntimeError("Invalid action")
