from typing import List

from common.script.script_dataclasses import IScriptEntry


class ScriptContainer(List[IScriptEntry]):
    def __init__(self):
        super(ScriptContainer, self).__init__()
