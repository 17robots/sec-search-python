import click
from time import sleep


def command_arguments(func):
    @click.command()
    @click.option('-sources', default=None, type=str, help='Name or ip of source vm', required=False)
    @click.option('-regions', default=None, type=str, help='Regions to filter by', required=False)
    @click.option('-dests',  default=None, type=str, help='Name or ip of dest vm', required=False)
    @click.option('-display',  default=None, type=str, help='AWS fields to show on output', required=False)
    @click.option('-accounts',  default=None, type=str, help='AWS accounts within user credentials to filter by', required=False)
    @click.option('-ports',  default=None, type=str, help='Ports to filter by', required=False)
    @click.option('-protocols',  default=None, type=str, help='Protocols to filter by', required=False)
    @click.option('-output', default=None, type=str, help="File to output results of command to")
    @click.option('-query', default=None, type=str, help="Cloudwatch Query for Watch Command")
    def wrapped_func(*args, **kwargs):
        func(*args, **kwargs)
    return wrapped_func


def listParams(paramArr):
    subcommand, sources, regions, dests, display, accounts, protocols, ports, output, query = paramArr
    return dict({
        'subcommand': subcommand,
        'sources': sources,
        'regions': regions,
        'dests': dests,
        'display': display,
        'accounts': accounts,
        'protocols': protocols,
        'ports': ports,
        'output': output,
        'cloudQuery': query
    })
