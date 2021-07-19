from .component import Component


class SearchStatus(Component):
    def __init__(self, props=None):
        self.state = props

    def render(self):
        return "Searching {} Instance {}".format(self.state['account'], self.state['instance'])
