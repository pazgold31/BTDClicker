class GuiParsers:
    @staticmethod
    def parse_selected_hero(hero_str: str) -> str:
        return hero_str.split(":")[0]

    @staticmethod
    def parse_selected_tower(tower_str: str) -> str:
        tower_name = tower_str.split(":")[0]
        return "Hero" if "Hero" in tower_name else tower_name

    @staticmethod
    def parse_existing_tower(tower_str: str) -> str:
        return tower_str.split("|")[0]
