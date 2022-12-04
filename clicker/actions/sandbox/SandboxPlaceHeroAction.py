from ahk import AHK

from clicker.actions.general.PlaceHeroAction import PlaceHeroAction
from common.game_classes.script.game_metadata_dataclasses import GameMetadata
from common.game_classes.tower import BaseTower


class SandboxPlaceHeroAction(PlaceHeroAction):

    def __init__(self, ahk: AHK, metadata: GameMetadata, hero: BaseTower):
        super(SandboxPlaceHeroAction, self).__init__(ahk=ahk, metadata=metadata, hero=hero)

    def can_act(self) -> bool:
        return True
