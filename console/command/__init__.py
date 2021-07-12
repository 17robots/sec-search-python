from console.command.search import searchCommand
from console.command.watch import watchCommand
import click

@click.group()
def cli():
    pass
cli.add_command(searchCommand, 'search')
cli.add_command(watchCommand, 'watch')