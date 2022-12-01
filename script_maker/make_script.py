from argparse import ArgumentParser, Namespace
from pathlib import Path

from script_maker.gui.gui_class import GuiClass


def parse_args() -> Namespace:
    argument_parser = ArgumentParser("BTD6 script maker")
    argument_parser.add_argument("-i", "--import-script", type=Path, required=False, default=None)
    return argument_parser.parse_args()


def main():
    args = parse_args()
    gui_class = GuiClass()
    if args.import_script:
        gui_class.import_script(script_path=args.import_script)
    gui_class.run()


if __name__ == '__main__':
    main()
