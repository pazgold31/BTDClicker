class IAction:
    def act(self) -> None:
        raise NotImplementedError

    def can_act(self) -> bool:
        raise NotImplementedError
