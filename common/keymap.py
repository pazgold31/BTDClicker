from common.enums import UpgradeTier


class Keymap:
    hero = "U"
    dart_monkey = "Q"
    boomerang = "W"
    bomb_shooter = "E"
    tack_shooter = "R"
    ice_monkey = "T"
    glue_gunner = "Y"
    sniper_monkey = "Z"
    monkey_sub = "X"
    monkey_buccaneer = "C"
    monkey_ace = "V"
    heli_pilot = "B"
    mortar_monkey = "N"
    dartling_gunner = "M"
    wizard_monkey = "A"
    super_monkey = "S"
    ninja_monkey = "D"
    alchemist = "F"
    druid = "G"
    banana_farm = "H"
    spike_factory = "J"
    monkey_village = "K"
    engineer_monkey = "L"

    upgrade_top = ","
    upgrade_middle = "."
    upgrade_bottom = "/"
    sell = "{BackSpace}"
    start = "{Space}"
    pause = "{Esc}"
    change_targeting = "{Tab}"
    change_special_targeting = "{PgDn}"


TOWER_KEY_MAP = {
    "Hero": Keymap.hero,
    "Dart Monkey": Keymap.dart_monkey,
    "Boomerang Monkey": Keymap.boomerang,
    "Bomb Shooter": Keymap.bomb_shooter,
    "Tack Shooter": Keymap.tack_shooter,
    "Ice Monkey": Keymap.ice_monkey,
    "Glue Gunner": Keymap.glue_gunner,
    "Sniper Monkey": Keymap.sniper_monkey,
    "Monkey Sub": Keymap.monkey_sub,
    "Monkey Buccaneer": Keymap.monkey_buccaneer,
    "Monkey Ace": Keymap.monkey_ace,
    "Heli Pilot": Keymap.heli_pilot,
    "Mortar Monkey": Keymap.mortar_monkey,
    "Dartling Gunner": Keymap.dartling_gunner,
    "Wizard Monkey": Keymap.wizard_monkey,
    "Super Monkey": Keymap.super_monkey,
    "Ninja Monkey": Keymap.ninja_monkey,
    "Alchemist": Keymap.alchemist,
    "Druid": Keymap.druid,
    "Banana Farm": Keymap.banana_farm,
    "Spike Factory": Keymap.spike_factory,
    "Monkey Village": Keymap.monkey_village,
    "Engineer Monkey": Keymap.engineer_monkey
}

UPGRADE_TIER_MAPPING = {
    UpgradeTier.top: Keymap.upgrade_top,
    UpgradeTier.middle: Keymap.upgrade_middle,
    UpgradeTier.bottom: Keymap.upgrade_bottom,
}
