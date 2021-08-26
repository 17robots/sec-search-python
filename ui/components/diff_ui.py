from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from .component import Component


class DiffUI(Component):
    def __init__(self, props):
        self.state = {
            'grp1Msgs': props['grp1Msgs'],
            'grp2Msgs': props['grp2Msgs'],
            'grp1': props['grp1'],
            'grp2': props['grp2']
        }

    def render(self):
        layout = Layout()
        layout.split_row(
            Layout(name='group1'),
            Layout(name='group2')
        )
        table1 = Table.grid()
        table1.add_column(self.state['grp1'])
        for msg in self.state['grp1Msgs']:
            table1.add_row(msg)

        table2 = Table.grid()
        table2.add_column(self.state['grp2'])
        for msg in self.state['grp2Msgs']:
            table2.add_row(msg)
        layout['group1'].update(Panel(table1))
        layout['group2'].update(Panel(table2))
        return layout
