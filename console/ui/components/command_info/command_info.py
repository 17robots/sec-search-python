from rich import box
from console.ui.components.component import Component
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class Command_Info(Component):
    def __init__(self, props: dict = None) -> None:
        super().__init__(props)
        self.state = None

    def render(self) -> Live:
        command_info = Table.grid(padding=1)
        command_info.add_column(justify='left')
        command_info.add_column(no_wrap=True)
        command_info.add_row(
            "Command:",
            self.props['subcommand']
        )
        command_info.add_row(
            "Source:",
            self.props['source']
        )
        command_info.add_row(
            "Dest:",
            self.props['destination'] if self.props['destination'] else 'None Specified'
        )
        command_info.add_row(
            "Ports:",
            self.props['ports'] if self.props['ports'] != None else 'None Specified'
        )
        command_info.add_row(
            "Accounts:",
            self.props['accounts'] if self.props['accounts'] != None else 'None Specified'
        )
        command_info.add_row(
            "Fields:",
            self.props['fields'] if self.props['fields'] != None else 'None Specified'
        )
        command_info.add_row(
            "Output File:",
            self.props['output'] if self.props['output'] != None else 'None Specified'
        )
        return Panel(command_info, box=box.ROUNDED,
                     padding=(1, 2), title="Command Info")
