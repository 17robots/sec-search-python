from aws.aws import AWS
from cli.common import command_arguments, listParams
from cli.cli import CLI
import common.event
from ui.app import App
import threading
import keyboard
from rich.live import Live
import gc

isRunning = True


def kill(threadEvent: threading.Event):
    global isRunning
    threadEvent.set()
    isRunning = False


@command_arguments
def watch(sources, regions, dests, display, accounts, ports, protocols, output, query):
    pump = common.event.MessagePump()
    state = dict({
        'regArr': {},
        'outputList': [],
        'outputColumns': [],
        'regionTotal': 0,
        'completedRegions': 0
    })

    def initState(e: common.event.InitEvent):
        state['regArr'][e.reg] = {}
        state['regArr'][e.reg]['total'] = 0
        state['regArr'][e.reg]['completed'] = 0
        state['regionTotal'] = e.regionTotal
        state['command'] = "watch"

    def startLog(e: common.event.LogStreamStarted):
        state['regArr'][e.region]['completed'] += 1

    def removeLogStream(e: common.event.LogStreamStopped):
        state['regArr'][e.region]['completed'] -= 1 if state['regArr'][e.region]['completed'] > 0 else 0

    def outputLog(e: common.event.LogEntryReceivedEvent):
        state['outputList'].append(e.log)

    def addStream(e: common.event.AddLogStream):
        state['regArr'][e.region]['total'] += e.amt

    def handleError(e: common.event.ErrorEvent):
        state['outputList'].append(str(e.e))

    pump.addListener(common.event.Events.InitEvent.value, initState)
    pump.addListener(common.event.Events.ErrorEvent.value, handleError)
    pump.addListener(common.event.Events.LogStreamStarted.value, startLog)
    pump.addListener(
        common.event.Events.LogStreamStopped.value, removeLogStream)
    pump.addListener(
        common.event.Events.LogEntryReceivedEvent.value, outputLog)
    pump.addListener(common.event.Events.AddLogStream.value, addStream)
    killEvent = threading.Event()

    def watchThread():
        try:
            cli = CLI(subcommand="watch", sources=sources, regions=regions, dests=dests,
                      protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
            aws = AWS()
            aws.watch(cli=cli, msgPmp=pump.messagePump, killEvent=killEvent)
        except Exception as e:
            pump.messagePump.put(common.event.ErrorEvent(e=e))

    thread = threading.Thread(target=watchThread, daemon=True)
    app = App(props=listParams(
        ["watch", sources, regions, dests, display, accounts, protocols, ports, output, query]))

    thread.start()

    with Live(app(), refresh_per_second=60, screen=True) as live:
        keyboard.add_hotkey(hotkey='q', callback=kill,
                            args=(killEvent,), suppress=True)
        while isRunning:
            live.update(app.setState(newState=state))
            pump.processEvents()
        thread.join()
        print("killing")
        gc.collect()
