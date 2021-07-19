from .component import Component
from .searchbarOutput import SearchbarOutput
from .watchLog import WatchLog


class WatchOutput(Component):
    def __init__(self, props=None):
        self.state = dict({
            'total': props['total'],
            'account': props['account'],
            'instance': props['instance'],
            'viewHeight': props['viewHeight'],
            'list': props['list']
        })
        self.searchbarOutput = SearchbarOutput(props=dict({
            'total': self.state['total'],
            'account': self.state['account'],
            'instance': self.state['instance']
        }))
        self.watchLog = WatchLog(props=dict({
            'viewHeight': self.state['viewHeight'],
            'list': self.state['list']
        }))

    def render(self):
        return self.watchLog.setState(newState=dict({
            'viewHeight': self.state['viewHeight'],
            'list': self.state['list']
        })) if self.finished() else self.searchbarOutput.setState(newState=dict({
            'account': self.state['account'],
            'instance': self.state['instance']
        }))

    def finished(self):
        return self.searchbarOutput.searchbar.progress.finished
