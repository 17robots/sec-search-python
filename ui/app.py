from ui.components.output import Output
from .components.component import Component
from rich.layout import Layout
from rich.panel import Panel
from .components.commandInfo import CommandInfo
from .components.status import ProgramInfo
import os


class App(Component):
    def __init__(self, props):
        self.param = props
        self.state = dict({
            'regArr': {},
            'finishedSearching': False,
            'outputList': [],
            'outputColumns': []
        })

        self.program = ProgramInfo()
        self.command = CommandInfo(props=self.param)
        self.output = Output(props=dict({
            'viewHeight': pollHeight(),
            'columns': self.state['outputColumns'],
            'messages': self.state['outputList']
        }))

    def render(self):
        layout = Layout()
        layout.split_row(
            Layout(name='sidebar'),
            Layout(name='main', ratio=3)
        )

        layout['sidebar'].split_column(
            Layout(name='command'),
            Layout(name='status')
        )
        layout['command'].update(Panel(self.command(), title="Command Info"))
        layout['status'].update(
            Panel(self.program.setState(newState=self.state), title="Progress"))

        layout['main'].update(
            Panel(self.Output(), title="Output"))
        return layout

    def Output(self):
        return self.output.setState(newState=dict({
            'viewHeight': pollHeight(),
            'columns': self.state['outputColumns'],
            'messages': self.state['outputList']
        }))


def pollHeight():
    return os.get_terminal_size().lines - 2
