from common.cost.cost_parsing import TOWER_COSTS
from common.enums import UpgradeTier
from common.script.script_dataclasses import CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, ChangeTargetingEntry, \
    ChangeSpecialTargetingEntry
from common.tower import Tower
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

    @property
    def towers_container(self) -> TowersContainer:
        return self._towers_container

    def is_hero_placeable(self) -> bool:
        # TODO: support sold hero
        return any(i for i in self._script_container if isinstance(i, CreateTowerEntry) and i.name == "Hero")

    def add_new_tower(self, name: str, x: int, y: int):
        tower_id = self._towers_container.add_new_tower(name=name, x=x, y=y)

        self._script_container.append(CreateTowerEntry(name=name, id=tower_id, x=x, y=y))

    def upgrade_tower(self, tower_id: int, tier: UpgradeTier):
        if not is_tier_upgradeable(tower=self._towers_container[tower_id], tier=tier):
            raise ValueError("Tier is at max level")

        self._towers_container[tower_id].tier_map[tier] += 1
        self.script_container.append(UpgradeTowerEntry(id=tower_id, tier=tier))

    def sell_tower(self, tower_id: int):
        additional_tower_info = self._towers_container.get_additional_tower_information()[tower_id]

        if additional_tower_info.sold:
            raise ValueError("Tower already sold")

        additional_tower_info.sold = True
        self._script_container.append(SellTowerEntry(id=tower_id))

    def change_targeting(self, tower_id: int):
        self._towers_container.get_additional_tower_information()[tower_id].targeting += 1
        self._script_container.append(ChangeTargetingEntry(id=tower_id))

    def change_special_targeting(self, tower_id: int):
        self._towers_container.get_additional_tower_information()[tower_id].s_targeting += 1
        self._script_container.append(ChangeSpecialTargetingEntry(id=tower_id))
