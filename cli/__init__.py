from cli.aws import aws
import click
from .search import search
from .watch import watch
from .aws import aws


@click.group()
def cli():
    pass


cli.add_command(search, 'search')
cli.add_command(watch, 'watch')
cli.add_command(aws, 'aws')
