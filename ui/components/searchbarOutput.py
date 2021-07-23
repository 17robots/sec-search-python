from .component import Component
from rich.table import Table
from .searchbar import Searchbar
from .searchStatus import SearchStatus


class SearchbarOutput(Component):
    def __init__(self, props=None):
        self.state = props
        self.searchstatus = SearchStatus()
        self.searchbar = Searchbar(props=dict(
            {'completed': props['completed']}))

    def render(self):
        table = Table.grid(padding=1)
        table.add_column('')
        table.add_column('')
        table.add_row(self.searchstatus(), self.searchbar.setState(
            newState=dict({'completed': self.state['completed']})))
        return table

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        return self()
