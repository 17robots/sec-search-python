from rich.table import Table
from .component import Component


class ProgramInfo(Component):
    def __init__(self, props=None):
        self.state = dict({
            'regArr': {},
            'finishedSearching': False
        })

    def render(self):
        table = Table.grid(expand=True)
        table.add_column("", justify='left')
        table.add_column("", justify='left')
        table.add_column("", justify='left')
        # TODO: Implement Based On State
        for region in self.state['regArr']:
            table.add_row(
                region, "{}/{}".format(self.state['regArr'][region]['completed'], self.state['regArr'][region]['total']), "{} results in {}s".format(self.state['regArr'][region]['results'], self.state['regArr'][region]['duration']) if self.state['regArr'][region]['finishedSearch'] else "")
            table.add_row("Current Account: ",
                          self.state['regArr'][region]['currAcct'], "")
        return table
