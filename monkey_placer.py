from ahk import AHK


def place_tower(x: int, y: int, keybind: str):
    ahk = AHK()
    ahk.mouse_position = (x, y)
    ahk.key_press(keybind)
    ahk.click()


def modify_tower():
    pass


ahk = AHK()
