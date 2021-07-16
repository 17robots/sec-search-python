from rich import box
from console.ui.components.component import Component
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class Program_Info(Component):
    def render(self) -> Panel:
        program_info = Table.grid(padding=1)
        program_info.add_column(justify='right')
        program_info.add_column(no_wrap=True)
        program_info.add_row(
            "Name:",
            "AWS Security Group Search"
        )
        program_info.add_row(
            "Version:",
            "0.0.1"
        )
        program_info.add_row(
            "Author:",
            "Matthew Dray"
        )
        return Panel(program_info, box=box.ROUNDED, padding=(1, 2), title="Program Info")
