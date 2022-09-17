import json
import re
from datetime import timedelta, datetime
from typing import List, Tuple, Dict, Union

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

from common.cost.cost_classes import Cost, Upgrade, UpgradeTierCost, UpgradesCost, TowerCost, HeroCost
from common.user_files import get_files_dir

BASE_WIKI_URL = r"https://bloons.fandom.com"
TOWERS_PRICES_URL = r"https://bloons.fandom.com/wiki/Tower_Price_Lists"
HERO_PRICES_URL = r"https://bloons.fandom.com/wiki/Heroes"

cost_re = re.compile(r"([\w .-]+)\nE\$([,\d]+)\**\nM\$([,\d]+)\**\nH\$([,\d]+)\**\nI\$([,\d]+)\**")

COSTS_UPDATE_TIME = timedelta(days=7)


def parse_single_upgrade(data: str) -> Upgrade:
    match = cost_re.search(data)
    return Upgrade(name=match.group(1), cost=Cost(
        easy=int(match.group(2).replace(",", "")),
        medium=int(match.group(3).replace(",", "")),
        hard=int(match.group(4).replace(",", "")),
        impopable=int(match.group(5).replace(",", ""))))


def parse_tower_base(data: str) -> Tuple[str, Cost]:
    match = cost_re.search(data)
    return match.group(1), Cost(
        easy=int(match.group(2).replace(",", "")),
        medium=int(match.group(3).replace(",", "")),
        hard=int(match.group(4).replace(",", "")),
        impopable=int(match.group(5).replace(",", "")))


def parse_upgrades_tier(data: List[str]) -> UpgradeTierCost:
    return UpgradeTierCost(first=parse_single_upgrade(data[-6]),
                           second=parse_single_upgrade(data[-5]),
                           third=parse_single_upgrade(data[-4]),
                           fourth=parse_single_upgrade(data[-3]),
                           fifth=parse_single_upgrade(data[-2]),
                           paragon=None)  # TODO: support paragons


def parse_upgrades(data: List[List[str]]) -> UpgradesCost:
    return UpgradesCost(top=parse_upgrades_tier(data[0]),
                        middle=parse_upgrades_tier(data[1]),
                        bottom=parse_upgrades_tier(data[2]))


def parse_data(data: List[List[str]]) -> List[TowerCost]:
    output: List[TowerCost] = []
    for i in range(0, len(data), 3):
        tower_lines = [data[i], data[i + 1], data[i + 2]]
        tower_name, tower_cost = parse_tower_base(tower_lines[0][0])
        output.append(TowerCost(name=tower_name, base_cost=tower_cost, upgrades=parse_upgrades(tower_lines)))

    return output


def _get_page_soup(url: str) -> BeautifulSoup:
    fake_ua = UserAgent()
    page = requests.get(url, headers={"User-Agent": fake_ua.chrome})
    return BeautifulSoup(page.content, "html.parser")


def parse_costs() -> List[TowerCost]:
    soup = _get_page_soup(TOWERS_PRICES_URL)
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


def parse_hero_costs() -> List[HeroCost]:
    soup = _get_page_soup(HERO_PRICES_URL)
    the_heroes_headline = None
    for headline in soup.find_all("h2"):
        if "The Heroes" in headline.text:
            the_heroes_headline = headline
            break

    if not the_heroes_headline:
        raise RuntimeError("Failed to find headline")

    prices_regex = re.compile(
        r"Default:\$([\d,]+) \(Easy\)\$([\d,]+) \(Medium\)\$([\d,]+) \(Hard\)\$([\d,]+) \(Impoppable\)")

    heroes = []
    for table in the_heroes_headline.find_all_next("table")[::2]:

        skins_headline = None
        for headline in table.find_previous_siblings("h2"):
            if "Hero Skins" in headline.text:
                skins_headline = headline
                break

        if skins_headline:
            break

        # noinspection PyUnresolvedReferences
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        link_element = rows[0].find("a")
        hero_name = link_element.text
        new_url = BASE_WIKI_URL + link_element.attrs["href"]

        try:
            hero_soup = _get_page_soup(new_url + "_(BTD6)")
            prices_box_text = hero_soup.find_all("div", class_="pi-data-value")[2].text
        except IndexError:
            hero_soup = _get_page_soup(new_url)
            prices_box_text = hero_soup.find_all("div", class_="pi-data-value")[2].text

        re_search = prices_regex.search(prices_box_text)
        heroes.append(HeroCost(name=hero_name, base_cost=Cost(easy=int(re_search.group(1).replace(",", "")),
                                                              medium=int(re_search.group(2).replace(",", "")),
                                                              hard=int(re_search.group(3).replace(",", "")),
                                                              impopable=int(re_search.group(4).replace(",", "")))))

    return heroes


def convert_to_map(lst: List[Union[HeroCost, TowerCost]]) -> Dict[str, Union[HeroCost, TowerCost]]:
    return {i.name: i for i in lst}


def get_hero_costs() -> Dict[str, HeroCost]:
    path = get_files_dir() / "hero_costs.json"
    try:
        if datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) < COSTS_UPDATE_TIME:
            with path.open("r") as of:
                return convert_to_map(parse_raw_as(List[HeroCost], of.read()))
    except FileNotFoundError:
        pass

    costs_data = parse_hero_costs()

    with path.open("w") as of:
        json.dump(costs_data, of, default=pydantic_encoder)

    return convert_to_map(costs_data)


def get_tower_costs() -> Dict[str, TowerCost]:
    path = get_files_dir() / "tower_costs.json"
    try:
        if datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) < COSTS_UPDATE_TIME:
            with path.open("r") as of:
                return convert_to_map(parse_raw_as(List[TowerCost], of.read()))
    except FileNotFoundError:
        pass

    costs_data = parse_costs()

    with path.open("w") as of:
        json.dump(costs_data, of, default=pydantic_encoder)

    return convert_to_map(costs_data)


