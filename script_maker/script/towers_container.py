import itertools
from collections import UserDict
from typing import Dict

from common.game_classes.tower import Tower, Hero, BaseTower
from script_maker.gui.gui_colors import EXISTING_TOWERS_COLORS


class TowersContainer(UserDict[int, BaseTower]):
    def __init__(self):
        super(TowersContainer, self).__init__()

        self._id_generator = itertools.count()

        self._colors_generator = itertools.chain(EXISTING_TOWERS_COLORS)
        self._colors_map: Dict[int, str] = {}

    def generate_new_id(self) -> int:
        return next(self._id_generator)

    def set_towers(self, value: Dict[int, Tower]):
        self.data = value

        self._id_generator = itertools.count(max(self.keys()) + 1)

    def add_new_tower(self, name: str, x: int, y: int, tower_id: int = None) -> int:
        tower_id = tower_id or self.generate_new_id()
        self[tower_id] = Tower(name=name, x=x, y=y)
        return tower_id

    def add_hero(self, x: int, y: int) -> int:
        tower_id = self.generate_new_id()
        self[tower_id] = Hero(x=x, y=y)
        return tower_id

    def get_tower_color(self, tower_id: int) -> str:
        if tower_id not in self._colors_map:
            self._colors_map[tower_id] = next(self._colors_generator)
            # TODO: remove print in the future
            print(f"Tower id: {tower_id} | {self._colors_map[tower_id]}")

        return self._colors_map[tower_id]
