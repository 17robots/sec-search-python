from rich.layout import Layout
from rich.table import Table
from .component import Component


class DiffUI(Component):
    def __init__(self, props):
        self.state = {
            'grp1Msgs': [],
            'grp2Msgs': [],
        }

    def render(self):
        layout = Layout()
        layout.split_row(
            Layout(name='group1'),
            Layout(name='group2')
        )
        table1 = Table()
        table1.add_column('')
        for msg in self.state['grp1Msgs']:
            table1.add_row(msg)

        table2 = Table()
        table2.add_column('')
        for msg in self.state['grp2Msgs']:
            table2.add_row(msg)
        layout['group1'].update(table1)
        layout['group2'].update(table2)
