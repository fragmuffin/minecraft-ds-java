from dataclasses import dataclass
from abc import ABC, abstractmethod

from logs import LogMessage


class Notifier(ABC):
    @classmethod
    @abstractmethod
    def from_environ(cls):
        # Return instance using defaults (eg: from os.environ, or preset files)
        # If there isn't enough information to create one, return None
        ...

    @abstractmethod
    def process(self, msg:LogMessage):
        # Decide what to do with msg... send or not?
        ...


notifiers = set()

def register(cls):
    if not issubclass(cls, Notifier):
        raise TypeError("expecting an instance of Notifier")
    notifiers.add(cls)
    return cls


def default_gen():
    for cls in notifiers:
        obj = cls.from_environ()
        if obj:
            yield obj