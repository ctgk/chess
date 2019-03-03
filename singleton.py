from chess import Chess


class Singleton:
    _chess = None

    @property
    def chess(self):
        if Singleton._chess is None:
            Singleton()
        return Singleton._chess

    def __init__(self):
        """ Virtually private constructor. """

        if Singleton._chess is not None:
            raise Exception("This class is a singleton!")
        else:
            Singleton._chess = Chess()
