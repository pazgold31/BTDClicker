from typing import Dict

from common.towers_info.info_classes import HeroInfo, TowerInfo
from common.towers_info.tower_info_crawling import get_heroes_info, get_towers_info

HEROES_INFO: Dict[str, HeroInfo] = get_heroes_info()
TOWERS_INFO: Dict[str, TowerInfo] = get_towers_info()
