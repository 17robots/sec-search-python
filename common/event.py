from dataclasses import dataclass, field
import queue
import enum


@dataclass
class Event:
    e_type: str
    pass


# search events

class Events(enum.Enum):
    InitEvent = "InitEvent"
    AccountStartedEvent = "AccountStartedEvent"
    AccounFinishedEvent = "AccounFinishedEvent"
    RegionFinishedEvent = "RegionFinishedEvent"
    SearchCompletedEvent = "SearchCompletedEvent"


@dataclass
class InitEvent(Event):
    reg: str
    acctTotal: int
    e_type: str = field(default=Events.InitEvent.value, init=False)


@dataclass
class AccountStartedEvent(Event):
    reg: str
    acctId: str
    e_type: str = field(default=Events.AccountStartedEvent.value, init=False)


@dataclass
class AccounFinishedEvent(Event):
    reg: str
    resTotal: int
    e_type: str = field(default=Events.AccounFinishedEvent.value, init=False)


@dataclass
class RegionFinishedEvent(Event):
    reg: str
    time: float
    e_type: str = field(default=Events.RegionFinishedEvent.value, init=False)


@dataclass
class SearchCompletedEvent(Event):
    finalResults: dict
    e_type: str = field(default=Events.SearchCompletedEvent.value, init=False)


# watch events


# pipeline
class MessagePump:
    def __init__(self) -> None:
        self.messagePump: queue.Queue = queue.Queue()
        self.listeners = {}

    def addListener(self, type, callback):
        self.listeners[type] = callback

    def processEvents(self):
        if self.messagePump.qsize() == 0:
            return
        event = self.messagePump.get()
        if event.e_type in self.listeners:
            self.listeners[event.e_type](event)
