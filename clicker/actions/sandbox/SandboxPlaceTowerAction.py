from ahk import AHK

from clicker.actions.general.PlaceTowerAction import PlaceTowerAction
from common.game_classes.enums import Difficulty
from common.game_classes.tower import Tower


class SandboxPlaceTowerAction(PlaceTowerAction):

    def __init__(self, ahk: AHK, difficulty: Difficulty, tower: Tower):
        super(SandboxPlaceTowerAction, self).__init__(ahk=ahk, difficulty=difficulty, tower=tower)

    def can_act(self) -> bool:
        return True
