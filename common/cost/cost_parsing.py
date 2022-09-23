import json
import re
from datetime import timedelta, datetime
from pathlib import Path
from typing import List, Tuple, Dict, TypeVar
from urllib.parse import urljoin

import bs4
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

from common.cost.cost_classes import Cost, Upgrade, UpgradeTierCost, UpgradesCost, TowerCost, HeroCost
from common.user_files import get_files_dir

BASE_WIKI_URL = r"https://bloons.fandom.com"
TOWERS_PRICES_URL = urljoin(BASE_WIKI_URL, r"wiki/Tower_Price_Lists")
HERO_PRICES_URL = urljoin(BASE_WIKI_URL, r"wiki/Heroes")

TOWER_COSTS_REGEX = re.compile(r"([\w .-]+)\nE\$([,\d]+)\**\nM\$([,\d]+)\**\nH\$([,\d]+)\**\nI\$([,\d]+)\**")
HERO_COSTS_REGEX = re.compile(
    r"Default:\$([\d,]+) \(Easy\)\$([\d,]+) \(Medium\)\$([\d,]+) \(Hard\)\$([\d,]+) \(Impoppable\)")

COSTS_UPDATE_TIME = timedelta(days=7)


def parse_single_upgrade(data: str) -> Upgrade:
    match = TOWER_COSTS_REGEX.search(data)
    return Upgrade(name=match.group(1), cost=Cost(
        easy=int(match.group(2).replace(",", "")),
        medium=int(match.group(3).replace(",", "")),
        hard=int(match.group(4).replace(",", "")),
        impopable=int(match.group(5).replace(",", ""))))


def parse_tower_base_cost(data: str) -> Tuple[str, Cost]:
    """
    :return: a tuple of the towers name and base cost.
    """
    match = TOWER_COSTS_REGEX.search(data)
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


def parse_towers_chunk(data: List[List[str]]) -> List[TowerCost]:
    output: List[TowerCost] = []
    for i in range(0, len(data), 3):
        tower_lines = [data[i], data[i + 1], data[i + 2]]
        tower_name, tower_cost = parse_tower_base_cost(tower_lines[0][0])
        output.append(TowerCost(name=tower_name, base_cost=tower_cost, upgrades=parse_upgrades(tower_lines)))

    return output


def get_page_soup(url: str) -> BeautifulSoup:
    fake_ua = UserAgent()
    page = requests.get(url, headers={"User-Agent": fake_ua.chrome})
    return BeautifulSoup(page.content, "html.parser")


def parse_towers_table(table_body: bs4.Tag) -> List[TowerCost]:
    rows = table_body.find_all('tr')
    towers_data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        towers_data.append([ele for ele in cols if ele])  # Get rid of empty values

    return parse_towers_chunk(data=towers_data[1:])  # remove the tower name item


def crawl_towers_costs() -> List[TowerCost]:
    soup = get_page_soup(TOWERS_PRICES_URL)
    tables = soup.find_all("table", class_="article-table")
    towers = []
    for table in tables[:4]:  # First 4 tables (primary, military, magic and support)
        towers.append(parse_towers_table(table_body=table.find('tbody')))

    return towers


def get_hero_headline_title(soup: BeautifulSoup):
    for headline in soup.find_all("h2"):
        if "The Heroes" in headline.text:
            return headline

    raise RuntimeError("Failed to find headline")


def get_hero_skins_title(table: bs4.Tag):
    for headline in table.find_previous_siblings("h2"):
        if "Hero Skins" in headline.text:
            return headline

    raise RuntimeError("Failed to find skins title")


def parse_hero_costs(table_body: bs4.Tag):
    rows = table_body.find_all('tr')
    link_element = rows[0].find("a")
    hero_name = link_element.text
    new_url = BASE_WIKI_URL + link_element.attrs["href"]

    try:
        hero_soup = get_page_soup(new_url + "_(BTD6)")
        prices_box_text = hero_soup.find_all("div", class_="pi-data-value")[2].text
    except IndexError:
        hero_soup = get_page_soup(new_url)
        prices_box_text = hero_soup.find_all("div", class_="pi-data-value")[2].text

    re_search = HERO_COSTS_REGEX.search(prices_box_text)
    return HeroCost(name=hero_name, base_cost=Cost(easy=int(re_search.group(1).replace(",", "")),
                                                   medium=int(re_search.group(2).replace(",", "")),
                                                   hard=int(re_search.group(3).replace(",", "")),
                                                   impopable=int(re_search.group(4).replace(",", ""))))


def crawl_hero_costs() -> List[HeroCost]:
    soup = get_page_soup(HERO_PRICES_URL)

    heroes = []
    for table in get_hero_headline_title(soup=soup).find_all_next("table")[::2]:
        try:
            # The hero skins headline comes after the prices.
            get_hero_skins_title(table=table)
            break
        except RuntimeError:
            pass

        table_body = table.find_next('tbody')
        heroes.append(parse_hero_costs(table_body=table_body))

    return heroes


CostType = TypeVar('CostType', HeroCost, TowerCost)


def convert_to_map(lst: List[CostType]) -> Dict[str, CostType]:
    return {i.name: i for i in lst}


def load_cached_costs(path: Path, output_type: CostType,
                      update_time: timedelta = COSTS_UPDATE_TIME) -> Dict[str, CostType]:
    if datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) < update_time:
        with path.open("r") as of:
            return convert_to_map(parse_raw_as(List[output_type], of.read()))


def save_cached_costs(path: Path, costs_data):
    with path.open("w") as of:
        json.dump(costs_data, of, default=pydantic_encoder)


def get_hero_costs() -> Dict[str, HeroCost]:
    path = get_files_dir() / "hero_costs.json"
    try:
        return load_cached_costs(path=path, output_type=HeroCost)
    except FileNotFoundError:
        costs_data = crawl_hero_costs()
        save_cached_costs(path=path, costs_data=costs_data)
        return convert_to_map(costs_data)


def get_tower_costs() -> Dict[str, TowerCost]:
    path = get_files_dir() / "tower_costs.json"
    try:
        return load_cached_costs(path=path, output_type=TowerCost)
    except FileNotFoundError:
        costs_data = crawl_hero_costs()
        save_cached_costs(path=path, costs_data=costs_data)
        return convert_to_map(costs_data)
