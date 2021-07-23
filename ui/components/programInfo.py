from rich.table import Table
from .component import Component


class ProgramInfo(Component):
    def __init__(self, props=None):
        self.state = dict({
            'acctArr': []
        })
    def render(self):
        table = Table.grid(padding=1, expand=True)
        table.add_column("", justify='center')
        table.add_column("", justify='center')
        table.add_column("", justify='center')
        for account in self.state['acctArr']:
            table.add_row(account['id'], "{}/{}".format(account['finishedCount'], account['totalCount']), "{} in {}S".format(account['resultCount'], account['duration']) if account['finishedCount'] == account['totalCount'] else "")
        return table
