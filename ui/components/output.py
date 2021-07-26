from .component import Component
from rich.table import Table


class Output(Component):
    def __init__(self, props=None):
        self.props = props
        self.state = dict({
            'viewHeight': props['viewHeight'],
            'columns': props['columns'],
            'messages': props['messages']
        })

    def render(self):
        table = Table(expand=True).grid()
        for col in self.state['columns']:
            table.add_column(col)
        for row in self.state['messages'][-self.state['viewHeight']:] if len(self.state['messages']) > self.state['viewHeight'] else self.state['messages']:
            table.add_row(row)
        return table
