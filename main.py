import json
import time
from typing import Dict

from ahk import AHK

from actions.PlaceTowerAction import PlaceTowerAction
from actions.UpgradeTowerAction import UpgradeTowerAction
from tower import Tower


def main():
    with open("exported.json", "r") as of:
        data = json.load(of)

    ahk = AHK()

    script = []
    tower_map: Dict[int, Tower] = {}
    for action in data:
        if action["action"] == "create":
            tower = Tower(name=action["name"], x=action["x"], y=action["y"])
            tower_map[action["id"]] = tower
            script.append(PlaceTowerAction(ahk=ahk, tower=tower))
        elif action["action"] == "upgrade":
            script.append(UpgradeTowerAction(ahk=ahk, tower=tower_map[action["id"]], tier=action["tier"]))

    pass

    time.sleep(2)

    for action in script:
        while True:
            if action.can_act():
                action.act()
                time.sleep(0.5)
                break


if __name__ == '__main__':
    main()
    print("Done")
