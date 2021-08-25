import click
from .search import search
from .watch import watch
from .diff import diff


@click.group()
def cli():
    pass


cli.add_command(search, 'search')
cli.add_command(watch, 'watch')
cli.add_command(diff, 'diff')
