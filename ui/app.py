from .components.component import Component
from rich.layout import Layout
from rich.panel import Panel
from .components.commandInfo import CommandInfo
from .components.programInfo import ProgramInfo
from .components.searchOutput import SearchOutput
from .components.watchOutput import WatchOutput
import os
from typing import Mapping

count = 0
demoCount = 1
environ: Mapping[str, str] = os.environ


class App(Component):
    def __init__(self, props):
        self.param = props
        self.program = ProgramInfo()
        self.command = CommandInfo(props=self.param)
        self.output = SearchOutput(props=dict({
            'completed': False
        })) if self.param['subcommand'] == 'search' else WatchOutput(props=dict({
            'total': 10,
            'account': pollAccount(),
            'instance': pollInstance(),
            'viewHeight': pollHeight(),
            'list': pollList()
        }))
        self.state = dict({
            'regArr': {},
            'finishedSearching': False,
            'results': []
        })

    def render(self):
        layout = Layout()
        layout.split_row(
            Layout(name='sidebar'),
            Layout(name='main', ratio=3)
        )

        layout['sidebar'].split_column(
            Layout(name='command'),
            Layout(name='program')
        )
        layout['command'].update(Panel(self.command(), title="Command Info"))
        layout['program'].update(
            Panel(self.program.setState(newState=self.state), title="Progress"))

        layout['main'].update(
            Panel(self.Output(), title="Output"))
        return layout

    def Output(self):
        global count
        count += 1
        return self.output.setState(newState=dict({
            'account': pollAccount(),
            'instance': pollInstance(),
            'results': pollResults(),
            'viewHeight': pollHeight(),
            'list': pollList()
        }))


def pollResults():
    global count
    if count % 2 == 0:
        return ['None', "{}".format(count)]
    return ['Cool Result', "{}".format(count)]


def pollAccount():
    global count
    if count % 5 == 0:
        return 'Hello'
    return 'World'


def pollInstance():
    global count
    if count % 2 == 0:
        return 'World'
    return 'Hello'


def pollList():
    retList = []
    global demoCount
    if count >= 11:
        for i in range(1, 50 if demoCount > 50 else demoCount, 1):
            retList.append('count val: {}'.format(i))
        demoCount += 1
    return retList


def pollHeight():
    return os.get_terminal_size().lines - 2
