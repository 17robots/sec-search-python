from console.ui.components.component import Component
from rich.panel import Panel
from rich.table import Table
from console.ui.components.output.searchbar_output.searchbar.searchbar import Searchbar
from console.ui.components.output.searchbar_output.search_status.search_status import Search_Status


class Searchbar_Output(Component):
    def __init__(self, props: dict = None):
        self.state = props
        self.searchbar = Searchbar(dict({
            'title': self.state['title'],
            'total': self.state['total'],
        }))
        self.search_status: Search_Status = Search_Status(dict({
            'account': self.state['account'],
            'instance': self.state['instance']
        }))

    def render(self):
        table = Table.grid(padding=1, expand=True)
        table.add_column("", justify="center")
        table.add_row(self.search_status.render())
        table.add_row(self.searchbar.render())
        return Panel(table)

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        self.searchbar.progress_task()
        return self.render()
