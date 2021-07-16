from console.ui.components.component import Component
from rich.panel import Panel
from rich.table import Table


class Search_Results(Component):
    def __init__(self, props: dict = None):
        self.props = props
        self.state = dict({
            'results': []
        })

    def render(self):
        resultsTable = Table.grid(padding=1)
        resultsTable.add_column("")
        for val in self.state['results']:
            resultsTable.add_row(val)
        return Panel(resultsTable)

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        return self.render()
