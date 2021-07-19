from .component import Component
from .searchbarOutput import SearchbarOutput
from .searchResults import SearchResults


class SearchOutput(Component):
    def __init__(self, props=None):
        self.state = dict({
            'total': props['total'],
            'account': props['account'],
            'instance': props['instance'],
            'results': []
        })
        self.searchbarOutput = SearchbarOutput(props=dict({
            'total': self.state['total'],
            'account': self.state['account'],
            'instance': self.state['instance']
        }))
        self.searchResults = SearchResults(props=dict({
            'results': self.state['results']
        }))

    def render(self):
        return self.searchResults.setState(newState=dict({
            'results': self.state['results']
        })) if self.finished() else self.searchbarOutput.setState(newState=dict({
            'account': self.state['account'],
            'instance': self.state['instance']
        }))

    def finished(self):
        return self.searchbarOutput.searchbar.progress.finished
