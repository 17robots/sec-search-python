from console.ui.components.component import Component
from rich.panel import Panel


class Search_Status(Component):
    def __init__(self, props: dict = None):
        self.message = "Searching Account {} Instance {} for rules".format(
            props['account'], props['instance'])
        self.panel = Panel(self.message)

    def render(self):
        return self.message

    def setState(self, newState):
        self.message = "Searching Account {} Instance {} for rules".format(
            newState['account'], newState['instance'])
        return self.render()
