from ahk import AHK

from clicker.actions.general.UpgradeTowerAction import UpgradeTowerAction
from common.game_classes.enums import Difficulty, UpgradeTier
from common.game_classes.tower import Tower


class SandboxUpgradeTowerAction(UpgradeTowerAction):
    def __init__(self, ahk: AHK, difficulty: Difficulty, tower: Tower, tier: UpgradeTier):
        super(SandboxUpgradeTowerAction, self).__init__(ahk=ahk, difficulty=difficulty, tower=tower, tier=tier)

    def can_act(self) -> bool:
        return True
