import itertools
from typing import Dict, Generator, Tuple

from common.game_classes.tower import Tower, Hero
from script_maker.gui.gui_colors import EXISTING_TOWERS_COLORS
from script_maker.script.additional_tower_info import AdditionalTowerInfo


class TowersContainer(Dict[int, Tower]):
    def __init__(self):
        super(TowersContainer, self).__init__()

        self._id_generator = itertools.count()
        self._additional_tower_information: Dict[int, AdditionalTowerInfo] = {}

        self._colors_generator = itertools.chain(EXISTING_TOWERS_COLORS)
        self._colors_map: Dict[int, str] = {}

    def set_towers(self, value: Dict[int, Tower]):
        super(TowersContainer, self).__init__(value)
        self._additional_tower_information = {i: AdditionalTowerInfo() for i in
                                              self.keys()}  # TODO: load the additional info
        self._id_generator = itertools.count(max(self.keys()) + 1)

    def add_new_tower(self, name: str, x: int, y: int) -> int:
        tower_id = next(self._id_generator)
        self[tower_id] = Tower(name=name, x=x, y=y)
        self._additional_tower_information[tower_id] = AdditionalTowerInfo()
        return tower_id

    def add_hero(self, name: str, x: int, y: int) -> int:
        tower_id = next(self._id_generator)
        self[tower_id] = Hero(name=name, x=x, y=y)
        self._additional_tower_information[tower_id] = AdditionalTowerInfo()
        return tower_id

    def get_tower_color(self, tower_id: int) -> str:
        if tower_id not in self._colors_map:
            self._colors_map[tower_id] = next(self._colors_generator)
            # TODO: remove print in the future
            print(f"Tower id: {tower_id} | {self._colors_map[tower_id]}")

        return self._colors_map[tower_id]

    def get_additional_tower_information(self) -> Dict[int, AdditionalTowerInfo]:
        return self._additional_tower_information

    def iter_with_additional_information(self) -> Generator[Tuple[int, Tower, AdditionalTowerInfo], None, None]:
        return ((tower_id, tower, self._additional_tower_information[tower_id]) for tower_id, tower in self.items())
