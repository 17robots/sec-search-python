from .component import Component
from rich.table import Table


class SearchResults(Component):
    def __init__(self, props=None):
        self.props = props
        self.state = dict({
            'results': []
        })

    def render(self):
        resultsTable = Table.grid(padding=1)
        resultsTable.add_column("")
        for val in self.state['results']:
            resultsTable.add_row(val)
        return resultsTable
