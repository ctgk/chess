from error import InvalidMove


class Memento:
    def __init__(self, state):
        self._state = state

    def get_state(self):
        return self._state


class CareTaker:
    _mementos = list()

    def push(self, memento):
        if len(self._mementos) == 2:
            self._mementos.pop(0)
        self._mementos.append(memento)

    def pop(self):
        try:
            return self._mementos.pop()
        except IndexError:
            raise InvalidMove
