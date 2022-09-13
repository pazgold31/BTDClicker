import itertools
from typing import Dict, Generator, Tuple

from common.tower import Tower
from script_maker.additional_tower_info import AdditionalTowerInfo


class TowersContainer(Dict[int, Tower]):
    def __init__(self):
        super(TowersContainer, self).__init__()

        self._id_generator = itertools.count()
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}

    def add_new_tower(self, name: str, x: int, y: int) -> int:
        tower_id = next(self._id_generator)
        self[tower_id] = Tower(name=name, x=x, y=y)
        self._additional_tower_information[tower_id] = AdditionalTowerInfo()
        return tower_id

    def get_additional_tower_information(self) -> Dict[int, AdditionalTowerInfo]:
        return self._additional_tower_information

    def iter_with_additional_information(self) -> Generator[Tuple[int, Tower, AdditionalTowerInfo], None, None]:
        return ((tower_id, tower, self._additional_tower_information[tower_id]) for tower_id, tower in self.items())
