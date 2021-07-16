from rich.live import Live
from console.command.common import command_arguments
from console.ui.components.app.app import App


@command_arguments
def watchCommand(source, dest, fields, accounts, ports, output):
    app = App(props=dict({
        'subcommand': 'watch',
        'source': source,
        'destination': dest,
        'ports': ports,
        'accounts': accounts,
        'fields': fields,
        'output': output
    }))

    with Live(app.render(), refresh_per_second=60, screen=True):
        while True:
            pass
