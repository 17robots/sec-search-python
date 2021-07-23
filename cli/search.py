from cli.common import command_arguments, listParams, kill
import keyboard
from ui.app import App
from rich.live import Live

isRunning = True
@command_arguments
def search(sources, regions, dests, display, accounts, ports, protocols, output, query):
    # thread here
    # start
    app = App(props=listParams(
        ["search", sources, regions, dests, display, accounts, protocols, ports, output, query]))
    keyboard.add_hotkey(hotkey='q', callback=kill, suppress=True)
    with Live(app(), refresh_per_second=60, screen=True) as live:
        while isRunning:
            live.update(app.setState(newState=None))
