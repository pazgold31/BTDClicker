import abc


class IAction(metaclass=abc.ABCMeta):
    def act(self) -> None:
        raise NotImplementedError

    def can_act(self) -> bool:
        raise NotImplementedError

    def get_action_message(self) -> str:
        raise NotImplementedError
