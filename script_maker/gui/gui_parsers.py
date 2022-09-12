class GuiParsers:
    @staticmethod
    def parse_selected_hero(hero_str: str) -> str:
        return hero_str.split(":")[0]

    @staticmethod
    def parse_selected_tower(hero_str: str) -> str:
        tower_name = hero_str.split(":")[0]
        return "Hero" if "Hero" in tower_name else tower_name
