import dataclasses
import json
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = r"https://bloons.fandom.com/wiki/Tower_Price_Lists"


@dataclass
class Cost:
    easy: int
    medium: int
    hard: int
    chimps: int

    def get_mapping(self) -> Dict[int, int]:
        return {1: self.easy, 2: self.medium, 3: self.hard, 4: self.chimps}


@dataclass
class Upgrade:
    name: str
    cost: Cost


@dataclass
class UpgradeTierCost:
    One: Cost
    Two: Cost
    Three: Cost
    Four: Cost
    Five: Cost
    Six: Optional[Cost]

    def get_mapping(self) -> Dict[int, Cost]:
        return {1: self.One, 2: self.Two, 3: self.Three, 4: self.Four, 5: self.Five, 6: self.Six}


@dataclass
class UpgradesCost:
    top: UpgradeTierCost
    mid: UpgradeTierCost
    bottom: UpgradeTierCost

    def get_mapping(self) -> Dict[int, UpgradeTierCost]:
        return {1: self.top, 2: self.mid, 3: self.top}


@dataclass
class TowerCost:
    name: str
    base_cost: Cost
    upgrades: UpgradesCost


cost_re = re.compile(r"([\w .]+)\nE\$([,\d]+)\**\nM\$([,\d]+)\**\nH\$([,\d]+)\**\nI\$([,\d]+)\**")


def parse_single_upgrade(data: str) -> Upgrade:
    match = cost_re.search(data)
    cost_args = (int(match.group(i).replace(",", "")) for i in range(2, 6))
    return Upgrade(match.group(1), Cost(*cost_args))


def parse_tower_base(data: str) -> Tuple[str, Cost]:
    match = cost_re.search(data)
    cost_args = (int(match.group(i).replace(",", "")) for i in range(2, 6))
    return match.group(1), Cost(*cost_args)


def parse_upgrades_tier(data: List[str]) -> UpgradeTierCost:
    return UpgradeTierCost(parse_single_upgrade(data[0]),
                           parse_single_upgrade(data[1]),
                           parse_single_upgrade(data[2]),
                           parse_single_upgrade(data[3]),
                           parse_single_upgrade(data[4]),
                           None)  # TODO: support paragons


def parse_upgrades(data: List[List[str]]) -> UpgradesCost:
    return UpgradesCost(parse_upgrades_tier(data[0]),
                        parse_upgrades_tier(data[1]),
                        parse_upgrades_tier(data[2]))


def parse_data(data: List[List[str]]) -> List[TowerCost]:
    output: List[TowerCost] = []
    for i in range(0, len(data), 3):
        tower_lines = [data[i], data[i + 1], data[i + 2]]
        tower_name, tower_cost = parse_tower_base(tower_lines[0][0])
        output.append(TowerCost(name=tower_name, base_cost=tower_cost, upgrades=parse_upgrades(tower_lines)))

    return output


def parse_costs() -> List[TowerCost]:
    fake_ua = UserAgent()
    page = requests.get(URL, headers={"User-Agent": fake_ua.chrome})
    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all("table", class_="article-table")
    towers = []
    for table in tables[:4]:
        data = []
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        towers += parse_data(data=data[1:])

    return towers


TOWER_COSTS: Dict[str, TowerCost] = {i.name: i for i in parse_costs()}


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

# with open("costs.json", "w") as of:
#     json.dump(parse_costs(), of, indent=4, cls=EnhancedJSONEncoder)
