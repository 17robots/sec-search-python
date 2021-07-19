from rich.table import Table
from .component import Component


class ProgramInfo(Component):
    def render(self):
        table = Table.grid(padding=1, expand=True)
        table.add_column("")
        table.add_column("", justify='center')
        table.add_row("Name:", "AWS Security Group Search")
        table.add_row("Version", "0.1.0")
        table.add_row("Creator", "Matthew")
        return table
