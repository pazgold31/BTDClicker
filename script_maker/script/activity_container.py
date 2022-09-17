import copy
from typing import List, Dict

from common.cost.game_costs import TOWER_COSTS
from common.game_classes.enums import UpgradeTier
from common.script.script_dataclasses import CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, \
    ChangeTargetingEntry, ChangeSpecialTargetingEntry, IScriptEntry
from common.game_classes.tower import Tower
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer


def is_tier_upgradeable(tower: Tower, tier: UpgradeTier) -> bool:
    current_upgrade = tower.tier_map[tier]
    try:
        new_cost = TOWER_COSTS[tower.name].upgrades.get_mapping()[tier].get_mapping()[current_upgrade + 1]
        return new_cost
    except KeyError:
        return False


class ActivityContainer:
    def __init__(self):
        self._script_container = ScriptContainer()
        self._towers_container = TowersContainer()

    @property
    def script_container(self) -> ScriptContainer:
        return self._script_container

    @script_container.setter
    def script_container(self, value: List[IScriptEntry]):
        self._script_container = value

    @property
    def towers_container(self) -> TowersContainer:
        return self._towers_container

    @towers_container.setter
    def towers_container(self, value: Dict[int, Tower]):
        self._towers_container.set_towers(value=value)

    def is_hero_placeable(self) -> bool:
        # TODO: support sold hero
        is_hero_placed = any(i for i in self._script_container if isinstance(i, CreateTowerEntry) and i.name == "Hero")
        return not is_hero_placed

    def _add_entry(self, entry: IScriptEntry, index: int):
        if not index:
            self._script_container.append(entry)
        else:
            self._script_container.insert(index, entry)

    def add_new_tower(self, name: str, x: int, y: int, index: int = None):
        tower_id = self._towers_container.add_new_tower(name=name, x=x, y=y)

        self._add_entry(CreateTowerEntry(name=name, id=tower_id, x=x, y=y), index=index)

    def add_hero(self, name: str, x: int, y: int, index: int = None):
        tower_id = self._towers_container.add_hero(name=name, x=x, y=y)

        self._add_entry(CreateTowerEntry(name=name, id=tower_id, x=x, y=y), index=index)

    def upgrade_tower(self, tower_id: int, tier: UpgradeTier, index: int = None):
        if not is_tier_upgradeable(tower=self._towers_container[tower_id], tier=tier):
            raise ValueError("Tier is at max level")

        self._towers_container[tower_id].tier_map[tier] += 1
        self._add_entry(UpgradeTowerEntry(id=tower_id, tier=tier), index=index)

    def sell_tower(self, tower_id: int, index: int = None):
        additional_tower_info = self._towers_container.get_additional_tower_information()[tower_id]

        if additional_tower_info.sold:
            raise ValueError("Tower already sold")

        additional_tower_info.sold = True
        self._add_entry(SellTowerEntry(id=tower_id), index=index)

    def change_targeting(self, tower_id: int, index: int = None):
        self._towers_container.get_additional_tower_information()[tower_id].targeting += 1
        self._add_entry(ChangeTargetingEntry(id=tower_id), index=index)

    def change_special_targeting(self, tower_id: int, index: int = None):
        self._towers_container.get_additional_tower_information()[tower_id].s_targeting += 1
        self._add_entry(ChangeSpecialTargetingEntry(id=tower_id), index=index)

    def delete_tower(self, tower_id: int):
        self._towers_container.pop(tower_id)
        for entry in copy.copy(self._script_container):
            if hasattr(entry, "id") and getattr(entry, "id") == tower_id:
                self._script_container.remove(entry)

    def delete_entry(self, entry_index: int):
        try:
            self._script_container.pop(entry_index)
        except IndexError:
            raise ValueError("Invalid entry index")

    def move_script_entry_up(self, entry_index: int):
        if entry_index == 0:
            raise ValueError("Entry is already at the top")

        self._script_container[entry_index], self._script_container[entry_index - 1] = \
            self._script_container[entry_index - 1], self._script_container[entry_index]

    def move_script_entry_down(self, entry_index: int):
        try:
            self._script_container[entry_index], self._script_container[entry_index + 1] = \
                self._script_container[entry_index + 1], self._script_container[entry_index]
        except IndexError:
            raise ValueError("Entry is already at the bottom")
