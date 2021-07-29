from aws.aws import AWS
from aws.sso import SSO
from cli.common import command_arguments
from cli.cli import CLI
import boto3
from aws.searchEnum import SearchFilters
from time import sleep
import threading


@command_arguments
def watch(sources, regions, dests, display, accounts, ports, protocols, output, query):
    cli = CLI(subcommand="search", sources=sources, regions=regions, dests=dests,
              protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
    aws = AWS()
    aws.watch(cli=cli)
