import click
from ui.app import App
from time import sleep
from rich.live import Live
import keyboard
import sys


def command_arguments(func):
    @click.command()
    @click.option('-sources', default=None, type=str, help='Name or ip of source vm', required=False)
    @click.option('-dests',  default=None, type=str, help='Name or ip of dest vm', required=False)
    @click.option('-display',  default=None, type=str, help='AWS fields to show on output', required=False)
    @click.option('-accounts',  default=None, type=str, help='AWS accounts within user credentials to filter by', required=False)
    @click.option('-ports',  default=None, type=str, help='Ports to filter by', required=False)
    @click.option('-protocols',  default=None, type=str, help='Protocols to filter by', required=False)
    @click.option('-output', default=None, type=str, help="File to output results of command to")
    def wrapped_func(*args, **kwargs):
        func(*args, **kwargs)
    return wrapped_func


def listParams(paramArr):
    subcommand, sources, dests, display, accounts, protocols, ports, output = paramArr
    return dict({
        'subcommand': subcommand,
        'sources': sources,
        'dests': dests,
        'display': display,
        'accounts': accounts,
        'protocols': protocols,
        'ports': ports,
        'output': output,
        'cloudQuery': None
    })


isRunning = True


def kill():
    global isRunning
    isRunning = False


def programLoop(subcommand, sources, dests, display, protocols, accounts, ports, output):
    global isRunning
    app = App(props=listParams(
        [subcommand, sources, dests, display, accounts, protocols, ports, output]))
    with Live(app(), refresh_per_second=60, screen=True) as live:
        while isRunning:
            if keyboard.is_pressed('q'):
                sys.exit(0)
            live.update(app())
            sleep(1)
