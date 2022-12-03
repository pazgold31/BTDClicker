import copy
from typing import List, Dict

from common.game_classes.enums import UpgradeTier
from common.game_classes.script.script_entries_dataclasses import IScriptEntry, PauseEntry, WaitForMoneyEntry, \
    ITowerModifyingScriptEntry, CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, \
    ChangeSpecialTargetingEntry, CreateHeroEntry
from common.game_classes.tower import Tower
from common.utils.upgrades_utils import is_tier_upgradeable
from script_maker.script.script_container import ScriptContainer
from script_maker.script.towers_container import TowersContainer


class ActivityContainer:
    def __init__(self):
        self._script_container = ScriptContainer()
        self._towers_container = TowersContainer()

    @property
    def script_container(self) -> ScriptContainer:
        return self._script_container

    @script_container.setter
    def script_container(self, value: list[IScriptEntry]):
        self._script_container = ScriptContainer(value)

    @property
    def towers_container(self) -> TowersContainer:
        return self._towers_container

    @towers_container.setter
    def towers_container(self, value: dict[int, Tower]):
        self._towers_container.set_towers(value=value)

    def reset_activity(self):
        self._script_container = ScriptContainer()
        self._towers_container = TowersContainer()

    def is_hero_placeable(self) -> bool:
        # TODO: support sold hero
        is_hero_placed = any(i for i in self._script_container if isinstance(i, CreateTowerEntry) and i.name == "Hero")
        return not is_hero_placed

    def _add_entry(self, entry: IScriptEntry, index: int):
        if not index:
            self._script_container.append(entry)
        else:
            self._script_container.insert(index, entry)

    def add_pause_entry(self, index: int = None):
        self._add_entry(PauseEntry(), index=index)

    def add_wait_for_money_entry(self, amount: int, index: int = None):
        self._add_entry(WaitForMoneyEntry(amount=amount), index=index)

    def add_new_tower(self, name: str, x: int, y: int, index: int = None, tower_id: int = None) -> int:
        tower_id = self._towers_container.add_new_tower(name=name, x=x, y=y, tower_id=tower_id)

        self._add_entry(CreateTowerEntry(name=name, id=tower_id, x=x, y=y), index=index)
        return tower_id

    def add_hero(self, x: int, y: int, index: int = None) -> int:
        tower_id = self._towers_container.add_hero(x=x, y=y)

        self._add_entry(CreateHeroEntry(id=tower_id, x=x, y=y), index=index)
        return tower_id

    def change_position(self, tower_id: int, x: int, y: int):
        self._towers_container[tower_id].x = x
        self._towers_container[tower_id].y = y
        self._script_container.change_position(tower_id=tower_id, x=x, y=y)

    def change_tower_type(self, tower_id: int, tower_type: str):
        tower = self._towers_container[tower_id]
        if not isinstance(tower, Tower):
            raise RuntimeError("Invalid tower!")

        tower.name = tower_type
        self._script_container.change_tower_type(tower_id=tower_id, tower_type=tower_type)

    def upgrade_tower(self, tower_id: int, tier: UpgradeTier, index: int = None):
        current_tower = self._towers_container[tower_id]
        if not isinstance(current_tower, Tower):
            raise TypeError("Cannot upgrade non-tower towers")

        if not is_tier_upgradeable(tower=current_tower, tier=tier):
            raise ValueError("Tier is at max level")

        current_tower.tier_map[tier] += 1
        self._add_entry(UpgradeTowerEntry(id=tower_id, tier=tier), index=index)

    def sell_tower(self, tower_id: int, index: int = None):
        if self._towers_container[tower_id].sold:
            raise ValueError("Tower already sold")

        self._towers_container[tower_id].sold = True
        self._add_entry(SellTowerEntry(id=tower_id), index=index)

    def change_targeting(self, tower_id: int, index: int = None):
        self._towers_container[tower_id].targeting += 1
        self._add_entry(ChangeTargetingEntry(id=tower_id), index=index)

    def change_special_targeting(self, tower_id: int, index: int = None):
        self._towers_container[tower_id].s_targeting += 1
        self._add_entry(ChangeSpecialTargetingEntry(id=tower_id), index=index)

    def delete_tower(self, tower_id: int):
        self._towers_container.pop(tower_id)
        for entry in self._script_container.get_entries_for_id(tower_id=tower_id):
            self._script_container.remove(entry)

    def delete_entry(self, entry_index: int):
        try:
            entry = self._script_container[entry_index]
            if isinstance(entry, CreateTowerEntry):
                if len(self._script_container.get_entries_for_id(tower_id=entry.id)) != 1:
                    raise ValueError

                self._towers_container.pop(entry.id)

            if isinstance(entry, UpgradeTowerEntry):
                current_tower = self._towers_container[entry.id]
                if not isinstance(current_tower, Tower):
                    raise TypeError("Upgrade entry on non-tower tower")
                current_tower.tier_map[entry.tier] -= 1
            elif isinstance(entry, SellTowerEntry):
                self._towers_container[entry.id].sold = False
            elif isinstance(entry, ChangeTargetingEntry):
                self._towers_container[entry.id].targeting -= 1
            elif isinstance(entry, ChangeSpecialTargetingEntry):
                self._towers_container[entry.id].s_targeting -= 1

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

    def duplicate_tower(self, tower_id: int, new_tower_x: int, new_tower_y: int, index: int = None):
        new_tower_id = self.duplicate_script_entries(
            entries=self._script_container.get_entries_for_id(tower_id=tower_id),
            new_index=index)
        self._towers_container[new_tower_id] = copy.copy(self._towers_container[tower_id])
        self._towers_container[new_tower_id].x = new_tower_x
        self._towers_container[new_tower_id].y = new_tower_y
        for entry in self._script_container.get_entries_for_id(tower_id=new_tower_id):
            if isinstance(entry, CreateTowerEntry):
                entry.x = new_tower_x
                entry.y = new_tower_y

    def duplicate_script_entry(self, entry: IScriptEntry, new_index: int = None, new_id: int = None):
        if isinstance(entry, ITowerModifyingScriptEntry):
            id_to_modify = new_id or entry.id
            if isinstance(entry, CreateTowerEntry):
                if not new_id or "Hero" == entry.name:
                    raise RuntimeError

                self.add_new_tower(name=entry.name, x=entry.x, y=entry.y, index=new_index, tower_id=id_to_modify)
            if isinstance(entry, UpgradeTowerEntry):
                self.upgrade_tower(tower_id=id_to_modify, tier=entry.tier, index=new_index)
            elif isinstance(entry, SellTowerEntry):
                self.sell_tower(tower_id=id_to_modify, index=new_index)
            elif isinstance(entry, ChangeTargetingEntry):
                self.change_targeting(tower_id=id_to_modify, index=new_index)
            elif isinstance(entry, ChangeSpecialTargetingEntry):
                self.change_special_targeting(tower_id=id_to_modify, index=new_index)
        else:
            raise RuntimeError

    def duplicate_script_entries(self, entries: list[IScriptEntry], new_index: int = None) -> int:
        new_tower_id = None
        if isinstance(entries[0], CreateTowerEntry):
            new_tower_id = self._towers_container.generate_new_id()

        for entry in entries:
            self.duplicate_script_entry(entry=entry, new_index=new_index, new_id=new_tower_id)
            if new_index is not None:
                new_index += 1

        return new_tower_id
