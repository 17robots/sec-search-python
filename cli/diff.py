import gc
from threading import Thread
from rich.live import Live
from cli.cli import CLI
import click
import common.event
from aws.aws import AWS
from ui.components.diff_ui import DiffUI


@click.command()
@click.argument('secid1')
@click.argument('secid2')
def diff(secid1, secid2):
    pump = common.event.MessagePump()
    state = {
        'grp1Msgs': ['Loading'],
        'grp2Msgs': ['Loading'],
        'grp1': secid1,
        'grp2': secid2
    }

    isRunning = True

    def groupNotFound(e: common.event.GroupNotFoundEvent):
        if e.group == 'group1':
            state['grp1Msgs'] = [f'Unable to find {secid1}']
        if e.group == 'group2':
            state['grp2Msgs'] = [f'Unable to find {secid2}']

    def loadDiffs(e: common.event.LoadDiffsEvent):
        state['grp1Msgs'] = e.grp1_diffs
        state['grp2Msgs'] = e.grp2_diffs

    def handleException(e: common.event.ErrorEvent):
        state['grp1Msgs'] = [str(e.e)]
        state['grp2Msgs'] = []

    pump.addListener(
        common.event.Events.GroupNotFoundEvent.value, groupNotFound)
    pump.addListener(common.event.Events.LoadDiffsEvent.value, loadDiffs)
    pump.addListener(common.event.Events.ErrorEvent.value, handleException)

    def diff_thread():
        try:
            cli = CLI(subcommand="diff", secid1=secid1, secid2=secid2)
            differ = AWS()
            differ.diff(cli=cli, msgPmp=pump.messagePump)
        except Exception as e:
            pump.messagePump.put(common.event.ErrorEvent(e=e))
    x = Thread(target=diff_thread, daemon=True)
    diff_ui = DiffUI(props=state)

    x.start()

    with Live(diff_ui(), refresh_per_second=60, screen=True) as live:
        while isRunning:
            live.update(diff_ui.setState(newState=state))
            pump.processEvents()
        x.join()
        gc.collect()
