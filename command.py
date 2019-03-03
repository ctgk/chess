import abc


class Invoker:
    def __init__(self):
        self._command = None

    def store_command(self, command):
        self._command = command

    def execute_commands(self):
        self._command.execute()


class Command(metaclass=abc.ABCMeta):
    def __init__(self, receiver):
        self._receiver = receiver

    @abc.abstractmethod
    def execute(self):
        pass


class ConcreteCommand(Command):
    def execute(self):
        if callable(self._receiver):
            self._receiver()
        else:
            raise NotImplementedError(f"receiver is not callable: {self._receiver}")
