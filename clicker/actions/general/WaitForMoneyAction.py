from ahk import AHK

from clicker.actions.IAction import IAction
from clicker.money_extracter import get_amount_of_money


class WaitForMoneyAction(IAction):

    def __init__(self, ahk: AHK, amount: int):
        self._ahk = ahk
        self._amount = amount

    def act(self):
        pass

    def can_act(self) -> bool:
        # noinspection PyBroadException
        try:
            money = get_amount_of_money()
            if money >= self._amount:
                return True

            return False
        except Exception:
            # TODO: add max tries
            pass

    def get_action_message(self) -> str:
        return f"Wait for {self._amount}$"
