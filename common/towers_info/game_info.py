from collections import UserDict

from common.towers_info.info_classes import HeroInfo, TowerInfo
from common.towers_info.tower_info_crawling import get_heroes_info, get_towers_info


class HeroesInfo(UserDict[str, HeroInfo]):
    def __init__(self):
        super(HeroesInfo, self).__init__(get_heroes_info())

    def update_info(self):
        self.data = get_heroes_info(force_scan=True)


class TowersInfo(UserDict[str, TowerInfo]):

    def __init__(self):
        super(TowersInfo, self).__init__(get_towers_info())

    def update_info(self):
        self.data = get_towers_info(force_scan=True)


g_heroes_info = HeroesInfo()
g_towers_info = TowersInfo()
