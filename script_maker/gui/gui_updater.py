import PySimpleGUI as sg

from common.script.script_dataclasses import GameMetadata, CreateTowerEntry, UpgradeTowerEntry, SellTowerEntry, \
    ChangeTargetingEntry, ChangeSpecialTargetingEntry
from script_maker.script.script_container import ScriptContainer
from script_maker.gui.gui_controls_utils import get_value_index_for_list_box
from script_maker.gui.gui_formatters import GuiFormatters
from script_maker.gui.gui_types import ValuesType
from script_maker.gui.gui_keys import GuiKeys
from script_maker.gui.gui_layout import get_tower_options, get_hero_options
from script_maker.script.towers_container import TowersContainer


class GuiUpdater:
    def __init__(self, window: sg.Window, metadata: GameMetadata):
        self._window = window
        self._metadata = metadata

    def update_difficulty(self, values: ValuesType):
        self._window[GuiKeys.TowerTypesListBox].update(
            get_tower_options(difficulty=self._metadata.difficulty, chosen_hero=self._metadata.hero_type), )
        selected_hero_index = self._window[GuiKeys.HeroListBox].Values.index(values[GuiKeys.HeroListBox])
        hero_options = get_hero_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.HeroListBox].update(values=hero_options, value=hero_options[selected_hero_index])

    def update_hero(self, metadata: GameMetadata):
        self._window[GuiKeys.TowerTypesListBox].update(get_tower_options(difficulty=metadata.difficulty,
                                                                         chosen_hero=metadata.hero_type), )

    def update_selected_tower_type(self, values: ValuesType, selected_tower_text: str):
        selected_tower_index = get_value_index_for_list_box(window=self._window, values=values,
                                                            key=GuiKeys.TowerTypesListBox)
        tower_options = get_tower_options(difficulty=self._metadata.difficulty)
        self._window[GuiKeys.TowerTypesListBox].update(None, tower_options[selected_tower_index])
        self._window[GuiKeys.NewTowerTypeInput].update(selected_tower_text, )

    def update_selected_existing_tower(self, selected_tower_text: str, is_hero: bool):
        self._window[GuiKeys.ExistingTowerName].update(selected_tower_text, )
        self._window[GuiKeys.TopUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.MiddleUpgradeButton].update(disabled=is_hero)
        self._window[GuiKeys.BottomUpgradeButton].update(disabled=is_hero)

    def update_existing_towers(self, towers_container: TowersContainer):
        list_box = self._window[GuiKeys.ExistingTowersListBox]
        list_box.update(GuiFormatters.format_existing_towers(towers_container), list_box.get_indexes())

    def update_script_box(self, script_container: ScriptContainer):
        output = []
        for action in script_container:
            if isinstance(action, CreateTowerEntry):
                output.append(f"Create: {action.name}({action.id}) | X: {action.x} Y: {action.y}")
            elif isinstance(action, UpgradeTowerEntry):
                output.append(f"Upgrade: ({action.id}) | tier: {action.tier}")
            elif isinstance(action, SellTowerEntry):
                output.append(f"Sell: ({action.id})")
            elif isinstance(action, ChangeTargetingEntry):
                output.append(f"Change targeting: ({action.id})")
            elif isinstance(action, ChangeSpecialTargetingEntry):
                output.append(f"Change special targeting: ({action.id})")

        self._window[GuiKeys.ScriptBox].update(output, )  # TODO: keep selection
