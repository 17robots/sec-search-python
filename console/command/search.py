from console.command.common import parseArr, command_arguments, parseArrArgs
from rich.live import Live
from console.ui.ui_main import build_ui
import rich

console = rich.console.Console()

@command_arguments
def searchCommand(source, dest, fields, accounts, ports):
    parsedFields, parsedAccounts, parsedPorts = parseArrArgs(fields, accounts, ports)
    layout = build_ui("search", source, dest, fields, accounts, ports)
    with Live(layout, refresh_per_second=60, screen=True):
        while True:
            pass

# def search_process(args: object):
