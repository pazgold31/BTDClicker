from collections import UserDict

from common.singleton import Singleton
from common.towers_info.info_classes import HeroInfo, TowerInfo
from common.towers_info.tower_info_crawling import get_heroes_info, get_towers_info


class HeroesInfo(UserDict[str, HeroInfo]):
    __metaclass__ = Singleton

    def __init__(self):
        super(HeroesInfo, self).__init__(get_heroes_info())

    def update_info(self):
        self.data = get_heroes_info(force_scan=True)


class TowersInfo(UserDict[str, TowerInfo]):
    __metaclass__ = Singleton

    def __init__(self):
        super(TowersInfo, self).__init__(get_towers_info())

    def update_info(self):
        self.data = get_towers_info(force_scan=True)
