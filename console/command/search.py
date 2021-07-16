from rich.live import Live
from console.command.common import command_arguments
from console.ui.components.app.app import App
from time import sleep


@command_arguments
def searchCommand(source, dest, fields, accounts, ports, output):
    app = App(props=dict({
        'subcommand': 'search',
        'source': source,
        'destination': dest,
        'ports': ports,
        'accounts': accounts,
        'fields': fields,
        'output': output
    }))

    with Live(app.render(), refresh_per_second=60, screen=True) as live:
        while True:
            live.update(app.poll())
            sleep(.01)
