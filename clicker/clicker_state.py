class ClickerState:
    def __init__(self):
        self._stopped = False

    def stop(self):
        print("Stop")
        self._stopped = True

    def run(self):
        print("Running")
        self._stopped = False

    def is_stopped(self):
        return self._stopped


g_clicker_state = ClickerState()
