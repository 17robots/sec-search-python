from .component import Component
from rich.table import Table
from .searchbar import Searchbar
from .searchStatus import SearchStatus


class SearchbarOutput(Component):
    def __init__(self, props=None):
        self.state = props
        self.searchstatus = SearchStatus(props=dict({
            'total': props['total'],
            'account': self.state['account'],
            'instance': self.state['instance']
        }))
        self.searchbar = Searchbar(props=dict({
            'total': self.state['total']
        }))

    def render(self):
        table = Table.grid(padding=1)
        table.add_column('')
        table.add_column('')
        table.add_row(self.searchstatus.setState(newState=dict({'account': self.state['account'], 'instance': self.state['instance']})),
                      self.searchbar())
        return table

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        self.searchbar.progress_task()
        return self()
