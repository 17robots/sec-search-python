from rich.console import JustifyMethod
from .component import Component
from rich.progress import Progress, SpinnerColumn, TextColumn


class Searchbar(Component):
    def __init__(self, props=None):
        self.props = props
        self.progress = Progress(
            SpinnerColumn(),
        )
        self.task = self.progress.add_task(
            description="", total=props['total'], justify='right'
        )

    def render(self):
        return self.progress

    def progress_task(self):
        self.progress.update(self.task, advance=1)
