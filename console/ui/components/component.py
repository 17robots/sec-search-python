from rich.live import Live
from rich.panel import Panel


class Component:
    def __init__(self, props: dict = None) -> None:
        self.props = props
        self.state = None

    def setState(self, newState):
        for key in newState:
            self.state[key] = newState[key]
        return self.render()

    def render(self):
        pass

    def pollProps(self, props):
        self.props = props
        self.live.update(self.render())
