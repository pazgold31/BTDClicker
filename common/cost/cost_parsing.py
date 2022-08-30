import re
from typing import List, Tuple, Dict

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from common.cost.cost_classes import Cost, Upgrade, UpgradeTierCost, UpgradesCost, TowerCost

URL = r"https://bloons.fandom.com/wiki/Tower_Price_Lists"

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
    for table in tables[:4]:  # First 4 tables (primary, military, magic and support)
        data = []
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        towers += parse_data(data=data[1:])  # remove the tower name item

    return towers


TOWER_COSTS: Dict[str, TowerCost] = {i.name: i for i in parse_costs()}
