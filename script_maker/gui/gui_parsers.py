class GuiParsers:
    @staticmethod
    def parse_hero(hero_str: str) -> str:
        return hero_str.split(":")[0]
