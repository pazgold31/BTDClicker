from typing import List

from common.game_classes.script.script_dataclasses import IScriptEntry


class ScriptContainer(List[IScriptEntry]):
    def __init__(self):
        super(ScriptContainer, self).__init__()
