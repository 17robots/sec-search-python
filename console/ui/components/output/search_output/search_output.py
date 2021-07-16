from console.ui.components.component import Component
from console.ui.components.output.searchbar_output.searchbar_output import Searchbar_Output
from console.ui.components.output.search_results.search_results import Search_Results


class Search_Output(Component):
    def __init__(self, props):
        self.state = dict({
            'title': props['title'],
            'total': props['total'],
            'account': props['account'],
            'instance': props['instance'],
            'results': []
        })
        self.searchbar_output = Searchbar_Output(props=dict({
            'title': self.state['title'],
            'total': self.state['total'],
            'account': self.state['account'],
            'instance': self.state['instance']
        }))
        self.search_results = Search_Results(props=dict({
            'results': self.state['results']
        }))

    def render(self):
        return self.search_results.setState(newState=dict({'results': self.state['results']})) if self.searchbar_output.searchbar.progress.finished else self.searchbar_output.setState(self.state)

    def setState(self, newState):
        if 'results' in newState.keys():
            self.state['results'] = newState['results']
            return self.render()
        else:
            for key in newState:
                self.state[key] = newState[key]
            return self.render()

    def finished(self):
        return self.searchbar_output.searchbar.progress.finished
