from common.script.script_dataclasses import CreateTowerEntry
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer


class ActivityContainer:
    def __init__(self):
        self._script_container = ScriptContainer()
        self._towers_container = TowersContainer()

    @property
    def script_container(self) -> ScriptContainer:
        return self._script_container

    @property
    def towers_container(self) -> TowersContainer:
        return self._towers_container

    def is_hero_placeable(self) -> bool:
        # TODO: support sold hero
        return any(i for i in self._script_container if isinstance(i, CreateTowerEntry) and i.name == "Hero")

    def add_new_tower(self, name: str, x: int, y: int):
        tower_id = self._towers_container.add_new_tower(name=name, x=x, y=y)

        self._script_container.append(CreateTowerEntry(name=name, id=tower_id, x=x, y=y))
