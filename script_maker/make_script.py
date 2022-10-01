from common.hotkeys import Hotkeys
from script_maker.gui.gui_class import GuiClass


def x(k: str):
    print(f"Hello: {k}")


def main():
    Hotkeys.add_hotkey('k', lambda: x(k="k"))
    Hotkeys.add_hotkey('c', lambda: x(k="c"))
    gui_class = GuiClass()
    gui_class.run()


if __name__ == '__main__':
    main()
