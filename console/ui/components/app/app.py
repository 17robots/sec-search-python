from console.ui.components.output.search_results.search_results import Search_Results
from console.ui.components.output.searchbar_output.searchbar_output import Searchbar_Output
from console.ui.components.program_info.program_info import Program_Info
from console.ui.components.command_info.command_info import Command_Info
from console.ui.components.component import Component
from rich.layout import Layout
from console.ui.components.output.search_output.search_output import Search_Output
search_results = Search_Results()

results = ['No Results', ]
currentAccount = 'hello'
currentInstance = 'world'

searchbar_output = Searchbar_Output(props=dict({
    'title': 'Searching',
    'total': 100,
    'account': currentAccount,
    'instance': currentInstance
}))

search_output = Search_Output(props=dict({
    'title': 'Searching',
    'total': 100,
    'account': 'Account 1',
    'instance': 'Instance 1',
}))


class App(Component):
    def __init__(self, props):
        self.props = props
        self.running = True
        self.state = None

    def render(self):
        layout = Layout(name="main")
        layout.split_row(
            Layout(name='sidebar'),
            Layout(name='output', ratio=3)
        )
        layout['sidebar'].split_column(
            Layout(name='command'),
            Layout(name='program')
        )
        layout['command'].update(Command_Info(props=self.props).render())
        layout['program'].update(Program_Info().render())
        layout['output'].update(self.Output())
        return layout

    def poll(self):
        return self.render()

    def Output(self):
        global searchbar_output
        global search_results
        global results
        global currentInstance
        global currentAccount

        return search_output.setState(newState=dict({
            'title': 'Searching',
            'account': 'Um',
            'instance': 'Hi',
            'results': pollResults()
        }))


def search():
    global results
    pass


def pollResults():
    return ['No Results']


def watch():
    pass
