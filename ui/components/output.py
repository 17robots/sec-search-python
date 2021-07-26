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
        table.add_column('')
        colString = ""
        for column in self.state['columns']:
            colString += str(column) + ' '
        table.add_row(colString.strip(' '))
        for row in self.state['messages'][-self.state['viewHeight']:] if len(self.state['messages']) > self.state['viewHeight'] else self.state['messages']:
            table.add_row(row)
        return table
