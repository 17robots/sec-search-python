from aws.aws_search import AWS
from cli.cli import CLI
from cli.common import command_arguments, listParams, kill
import keyboard
from ui.app import App
from rich.live import Live
import threading
import common.event
import time

isRunning = True


@command_arguments
def search(sources, regions, dests, display, accounts, ports, protocols, output, query):
    pump = common.event.MessagePump()
    state = dict({
        'regArr': {},
        'finishedSearching': False,
        'results': []
    })

    def initState(e: common.event.InitEvent):
        state['regArr'][e.reg] = {}
        state['regArr'][e.reg]['total'] = e.acctTotal
        state['regArr'][e.reg]['completed'] = 0
        state['regArr'][e.reg]['results'] = 0
        state['regArr'][e.reg]['duration'] = 0
        state['regArr'][e.reg]['currAcct'] = 'None'
        state['regArr'][e.reg]['startTime'] = time.time()
        state['regArr'][e.reg]['finishedSearch'] = False

    def startAcct(e: common.event.AccountStartedEvent):
        state['regArr'][e.reg]['currAcct'] = e.acctId

    def finishAcct(e: common.event.AccounFinishedEvent):
        state['regArr'][e.reg]['results'] += e.resTotal
        state['regArr'][e.reg]['completed'] += 1
        if state['regArr'][e.reg]['completed'] == state['regArr'][e.reg]['total']:
            pump.messagePump.put(common.event.RegionFinishedEvent(
                reg=e.reg, time=time.time() - state['regArr'][e.reg]['startTime']))

    def finishRegion(e: common.event.RegionFinishedEvent):
        state['regArr'][e.reg]['duration'] = e.time
        state['regArr'][e.reg]['finishedSearch'] = True
        state['regArr'][e.reg]['currAcct'] = "Region Completed"

    def finishSearch(e: common.event.SearchCompletedEvent):
        state['finishedSearching'] = True
        state['results'] = e.finalResults

    # add eventlisteners
    pump.addListener(common.event.Events.InitEvent.value, initState)
    pump.addListener(
        common.event.Events.AccounFinishedEvent.value, finishAcct)
    pump.addListener(common.event.Events.AccountStartedEvent.value, startAcct)
    pump.addListener(
        common.event.Events.RegionFinishedEvent.value, finishRegion)
    pump.addListener(
        common.event.Events.SearchCompletedEvent.value, finishSearch)

    # main search thread
    def searchThread():
        cli = CLI(subcommand="search", sources=sources, regions=regions, dests=dests,
                  protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
        searcher = AWS()
        searcher.search(cli, pump.messagePump)

    thread = threading.Thread(target=searchThread, daemon=True)
    app = App(props=listParams(
        ["search", sources, regions, dests, display, accounts, protocols, ports, output, query]))

    thread.start()

    with Live(app(), refresh_per_second=60, screen=True) as live:
        keyboard.add_hotkey(hotkey='q', callback=kill, suppress=True)
        while isRunning:
            pump.processEvents()
            live.update(app.setState(newState=state))
