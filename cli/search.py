from aws.aws_search import AWS
from cli.cli import CLI
from cli.common import command_arguments, listParams
import keyboard
from ui.app import App
from rich.live import Live
import threading
import common.event
import time
import gc

isRunning = True

def kill():
    global isRunning
    isRunning = False

@command_arguments
def search(sources, regions, dests, display, accounts, ports, protocols, output, query):
    pump = common.event.MessagePump()
    state = dict({
        'regArr': {},
        'finishedSearching': False,
        'results': [],
        'regionTotal': 0,
        'completedRegions': 0
    })

    def initState(e: common.event.InitEvent):
        state['regArr'][e.reg] = {}
        state['regArr'][e.reg]['total'] = e.acctTotal
        state['regArr'][e.reg]['completed'] = 0
        state['regArr'][e.reg]['resultTotal'] = 0
        state['regArr'][e.reg]['duration'] = 0
        state['regArr'][e.reg]['currAcct'] = 'None'
        state['regArr'][e.reg]['startTime'] = time.time()
        state['regArr'][e.reg]['finishedSearch'] = False
        state['regionTotal'] = e.regionTotal

    def startAcct(e: common.event.AccountStartedEvent):
        pass
    def finishAcct(e: common.event.AccounFinishedEvent):
        state['regArr'][e.reg]['resultTotal'] += e.resTotal
        state['regArr'][e.reg]['completed'] += 1
        if state['regArr'][e.reg]['completed'] == state['regArr'][e.reg]['total']:
            pump.messagePump.put(common.event.RegionFinishedEvent(
                reg=e.reg, time=time.time() - state['regArr'][e.reg]['startTime']), block=False)

    def finishRegion(e: common.event.RegionFinishedEvent):
        state['regArr'][e.reg]['duration'] = e.time
        state['regArr'][e.reg]['finishedSearch'] = True
        state['regArr'][e.reg]['currAcct'] = "Region Completed"
        state['completedRegions'] += 1
        if state['completedRegions'] == state['regionTotal']:
            pump.messagePump.put(common.event.SearchCompletedEvent(), block=False)


    def finishSearch(e: common.event.SearchCompletedEvent):
        state['finishedSearching'] = True

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
        state['results'] = searcher.ruleMap['us-east-1']['995684153539']

    thread = threading.Thread(target=searchThread, daemon=True)
    app = App(props=listParams(
        ["search", sources, regions, dests, display, accounts, protocols, ports, output, query]))

    thread.start()

    with Live(app(), refresh_per_second=60, screen=True) as live:
        keyboard.add_hotkey(hotkey='q', callback=kill, suppress=True)
        while isRunning:
            live.update(app.setState(newState=state))
            pump.processEvents()
        thread.join()
        gc.collect()
