from dataclasses import dataclass, field
from logging import ERROR
import queue
import enum


@dataclass
class Event:
    e_type: str
    pass


class Events(enum.Enum):
    InitEvent = "InitEvent"
    AccountStartedEvent = "AccountStartedEvent"
    AccounFinishedEvent = "AccounFinishedEvent"
    RegionFinishedEvent = "RegionFinishedEvent"
    SearchCompletedEvent = "SearchCompletedEvent"
    ErrorEvent = "ErrorEvent"
    LoadResultsEvent = "LoadResultsEvent"
    LogEntryReceivedEvent = "LogEntryReceivedEvent"
    LogStreamStarted = "LogStreamStarted"
    LogStreamStopped = "LogStreamStopped"
    AddLogStream = "AddLogStream"

# error events


@dataclass
class ErrorEvent(Event):
    e: ERROR
    e_type: str = field(default=Events.ErrorEvent.value, init=False)

# general events


@dataclass
class InitEvent(Event):
    reg: str
    counterTotal: int
    regionTotal: int
    e_type: str = field(default=Events.InitEvent.value, init=False)

# search events


@dataclass
class AccountStartedEvent(Event):
    reg: str
    acctId: str
    e_type: str = field(default=Events.AccountStartedEvent.value, init=False)


@dataclass
class AccounFinishedEvent(Event):
    reg: str
    resTotal: int
    results: list
    e_type: str = field(default=Events.AccounFinishedEvent.value, init=False)


@dataclass
class RegionFinishedEvent(Event):
    reg: str
    time: float
    e_type: str = field(default=Events.RegionFinishedEvent.value, init=False)


@dataclass
class SearchCompletedEvent(Event):
    e_type: str = field(default=Events.SearchCompletedEvent.value, init=False)


@dataclass
class LoadResultsEvent(Event):
    results: dict
    e_type: str = field(default=Events.LoadResultsEvent.value, init=False)


# watch events

@dataclass
class LogEntryReceivedEvent(Event):
    log: str
    e_type: str = field(default=Events.LogEntryReceivedEvent.value, init=False)


@dataclass
class LogStreamStarted(Event):
    region: str
    e_type: str = field(default=Events.LogStreamStarted.value, init=False)


@dataclass
class AddLogStream(Event):
    region: str
    amt: int
    e_type: str = field(default=Events.AddLogStream.value, init=False)


@dataclass
class LogStreamStopped(Event):
    region: str
    e_type: str = field(default=Events.LogStreamStopped.value, init=False)

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
        event = self.messagePump.get(block=False)
        if event.e_type in self.listeners:
            self.listeners[event.e_type](event)
