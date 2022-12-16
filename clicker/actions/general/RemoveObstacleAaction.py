import time

import pyautogui
from PIL import Image
from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.money_extracter import get_amount_of_money
from common.user_files import get_const_images_dir
from common.utils.picture_processing.sub_image_utils import get_inner_image_position


class RemoveObstacleAction(IAction):
    CONFIRMATION_THRESHOLD = 0.1

    def __init__(self, ahk: AHK, x: int, y: int, cost: int):
        self._ahk = ahk
        self._x = x
        self._y = y
        self._cost = cost

        self._confirmation_image = Image.open(str(get_const_images_dir() / "remove_obstacle.PNG"))

    def act(self):
        self._ahk.mouse_position = (self._x, self._y)
        self._ahk.click()
        time.sleep(0.2)

        screenshot = pyautogui.screenshot()
        button_x, button_y = get_inner_image_position(image=screenshot, inner_image=self._confirmation_image,
                                                      threshold=self.CONFIRMATION_THRESHOLD)

        self._ahk.mouse_position = (button_x, button_y)
        self._ahk.click()
        time.sleep(0.2)

    def can_act(self) -> bool:
        # noinspection PyBroadException
        try:
            money = get_amount_of_money()
            if money >= self._cost:
                return True

            return False
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Remove obstacle for {self._cost}$"
