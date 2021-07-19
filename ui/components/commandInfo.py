from .component import Component
from rich.table import Table


class CommandInfo(Component):
    def render(self):
        table = Table.grid(padding=1, expand=True)
        table.add_column("")
        table.add_column("", justify='right')
        table.add_row(
            "subcommand", self.param['subcommand'] if self.param['subcommand'] != None else 'None Specified')
        table.add_row(
            "sources", self.param['sources'] if self.param['sources'] != None else 'None Specified')
        table.add_row(
            "dests", self.param['dests'] if self.param['dests'] != None else 'None Specified')
        table.add_row(
            "ports", self.param['ports'] if self.param['ports'] != None else 'None Specified')
        table.add_row(
            "accounts", self.param['accounts'] if self.param['accounts'] != None else 'None Specified')
        table.add_row(
            "display string", self.param['display'] if self.param['display'] != None else 'None Specified')
        table.add_row(
            "protocols", self.param['protocols'] if self.param['protocols'] != None else 'None Specified')
        table.add_row(
            "cloud query", self.param['cloudQuery'] if self.param['cloudQuery'] != None else 'None Specified')
        return table
