import re
from datetime import timedelta
from typing import List, Tuple, Dict, TypeVar, Type
from urllib.parse import urljoin

import bs4
from bs4 import BeautifulSoup

from common.game_classes.enums import TowerType
from common.towers_info.info_classes import Cost, Upgrade, UpgradeTierCost, UpgradesCost, TowerInfo, HeroInfo
from common.user_files import get_files_dir
from common.utils.cashed_dataclasses.cashed_dataclasses_utils import load_cached_dataclass, save_dataclass_to_cache
from common.wiki_crawl.crawling_utils import get_page_soup
from common.wiki_crawl.wiki_consts import BASE_WIKI_URL

TOWERS_PRICES_URL = urljoin(BASE_WIKI_URL, r"wiki/Tower_Price_Lists")
HERO_PRICES_URL = urljoin(BASE_WIKI_URL, r"wiki/Heroes")

TOWER_INFO_REGEX = re.compile(r"([\w .-]+)\nE\$([,\d]+)\**\nM\$([,\d]+)\**\nH\$([,\d]+)\**\nI\$([,\d]+)\**")
HERO_INFO_REGEX = re.compile(
    r"Default:\$([\d,]+) \(Easy\)\$([\d,]+) \(Medium\)\$([\d,]+) \(Hard\)\$([\d,]+) \(Impoppable\)")

INFO_UPDATE_TIME = timedelta(days=7)


def parse_single_upgrade(data: str) -> Upgrade:
    match = TOWER_INFO_REGEX.search(data)
    return Upgrade(name=match.group(1), cost=Cost(
        easy=int(match.group(2).replace(",", "")),
        medium=int(match.group(3).replace(",", "")),
        hard=int(match.group(4).replace(",", "")),
        impopable=int(match.group(5).replace(",", ""))))


def parse_tower_base_cost(data: str) -> Tuple[str, Cost]:
    """
    :return: a tuple of the towers name and base towers_info.
    """
    match = TOWER_INFO_REGEX.search(data)
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


def parse_towers_chunk(data: List[List[str]], towers_type: TowerType) -> List[TowerInfo]:
    output: List[TowerInfo] = []
    for i in range(0, len(data), 3):
        tower_lines = [data[i], data[i + 1], data[i + 2]]
        tower_name, tower_cost = parse_tower_base_cost(tower_lines[0][0])
        output.append(TowerInfo(name=tower_name, type=towers_type, base_cost=tower_cost,
                                upgrades=parse_upgrades(tower_lines)))

    return output


def parse_towers_table(table_body: bs4.Tag, towers_type: TowerType) -> List[TowerInfo]:
    rows = table_body.find_all('tr')
    towers_data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        towers_data.append([ele for ele in cols if ele])  # Get rid of empty values

    return parse_towers_chunk(data=towers_data[1:], towers_type=towers_type)  # remove the tower name item


def get_towers_type_name(table: bs4.Tag):
    for headline in table.find_previous("h3"):
        return headline.text

    raise RuntimeError("Failed to find headline")


def get_tower_type(tower_type_name: str) -> TowerType:
    return {"Primary Monkeys": TowerType.Primary,
            "Military Monkeys": TowerType.Military,
            "Magic Monkeys": TowerType.Magic,
            "Support Monkeys": TowerType.Support}[tower_type_name]


def crawl_towers_info() -> List[TowerInfo]:
    soup = get_page_soup(TOWERS_PRICES_URL)
    tables = soup.find_all("table", class_="article-table")
    towers = []
    for table in tables[:4]:  # First 4 tables (primary, military, magic and support)
        towers += parse_towers_table(table_body=table.find('tbody'),
                                     towers_type=get_tower_type(get_towers_type_name(table=table)))

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


def parse_hero_info(table_body: bs4.Tag):
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

    re_search = HERO_INFO_REGEX.search(prices_box_text)
    return HeroInfo(name=hero_name, base_cost=Cost(easy=int(re_search.group(1).replace(",", "")),
                                                   medium=int(re_search.group(2).replace(",", "")),
                                                   hard=int(re_search.group(3).replace(",", "")),
                                                   impopable=int(re_search.group(4).replace(",", ""))))


def crawl_hero_info() -> List[HeroInfo]:
    soup = get_page_soup(HERO_PRICES_URL)

    heroes = []
    for table in get_hero_headline_title(soup=soup).find_all_next("table")[::2]:
        try:
            # The hero skins headline comes after the prices.
            # noinspection PyTypeChecker
            get_hero_skins_title(table=table)
            break
        except RuntimeError:
            pass

        table_body = table.find_next('tbody')
        heroes.append(parse_hero_info(table_body=table_body))

    return heroes


OutputInfoType = TypeVar('OutputInfoType', Type[HeroInfo], Type[TowerInfo])
InfoType = TypeVar('InfoType', HeroInfo, TowerInfo)


def convert_to_map(lst: List[InfoType]) -> Dict[str, InfoType]:
    return {i.name: i for i in lst}


def get_heroes_info(force_scan: bool = False) -> Dict[str, HeroInfo]:
    path = get_files_dir() / "heroes_info.json"
    if not force_scan:
        try:
            return convert_to_map(
                load_cached_dataclass(path=path, output_type=List[HeroInfo], update_time=INFO_UPDATE_TIME))
        except (FileNotFoundError, TypeError):
            pass

    info_data = crawl_hero_info()
    save_dataclass_to_cache(path=path, info_data=info_data)
    return convert_to_map(info_data)


def get_towers_info(force_scan: bool = False) -> Dict[str, TowerInfo]:
    path = get_files_dir() / "towers_info.json"
    if not force_scan:
        try:
            return convert_to_map(load_cached_dataclass(path=path, output_type=List[TowerInfo],
                                                        update_time=INFO_UPDATE_TIME))
        except (FileNotFoundError, TypeError):
            pass

    info_data = crawl_towers_info()
    save_dataclass_to_cache(path=path, info_data=info_data)
    return convert_to_map(info_data)
