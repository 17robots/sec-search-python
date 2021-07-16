from console.ui.components.component import Component
from rich.progress import Progress
from rich.panel import Panel


class Searchbar(Component):
    def __init__(self, props):
        self.progress = Progress(expand=True)
        self.task = self.progress.add_task(
            props['title'], total=props['total'], expand=True)
        self.state = None

    def render(self):
        return self.progress

    def progress_task(self):
        self.progress.update(self.task, advance=1)
