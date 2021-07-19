from .component import Component
from rich.table import Table


class WatchLog(Component):
    def __init__(self, props=None):
        self.props = props
        self.state = dict({
            'viewHeight': props['viewHeight'],
            'list': props['list']
        })

    def render(self):
        table = Table(expand=True).grid()
        table.add_column('')
        for row in self.state['list'][-self.state['viewHeight']:] if len(self.state['list']) > self.state['viewHeight'] else self.state['list']:
            table.add_row(row)
        return table
