from cli.cli import CLI
import click
import common.event
from aws.aws import AWS


@click.command()
@click.argument('secid1')
@click.argument('secid2')
def diff(secid1, secid2):
    pump = common.event.MessagePump()
    state = dict({
        'regArr': {},
        'outputList': [],
        'outputColumns': [],
        'regionTotal': 0,
        'completedRegions': 0
    })

    def diff_thread():
        try:
            cli = CLI(subcommand="diff", secid1=secid1, secid2=secid2)
            differ = AWS()
            differ.diff()
        except Exception as e:
            pump.messagePump.put(common.event.ErrorEvent)
