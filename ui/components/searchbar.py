from rich.console import JustifyMethod
from .component import Component
from rich.progress import Progress, SpinnerColumn, TextColumn


class Searchbar(Component):
    def __init__(self, props=None):
        self.state = dict({
            'completed': props['completed']
        })
        self.props = props
        self.progress = Progress(
            SpinnerColumn(),
        )
        self.task = self.progress.add_task(
            description="", total=100, justify='right'
        )

    def render(self):
        return self.progress

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        if self.state['completed']:
            self.progress.update(completed=True)
