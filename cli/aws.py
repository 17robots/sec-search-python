from cli.cli import CLI
from .common import command_arguments
from aws.aws_search import AWS

@command_arguments
def aws(sources, regions, dests, display, accounts, ports, protocols, output, query):
    cli = CLI(subcommand="demo", sources=sources, regions=regions, dests=dests, protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
    searcher = AWS()
    searcher.search(cli)

    print('Before Filtering')
    for region in searcher.ruleMap:
        for account in searcher.ruleMap[region]:
            print("{} account {}: {} rules".format(region, account, len(searcher.ruleMap[region][account])))

    
    for region in searcher.ruleMap:
        for account in searcher.ruleMap[region]:
            searcher.ruleMap[region][account] = list(filter(cli.filterSources, searcher.ruleMap[region][account]))
            searcher.ruleMap[region][account] = list(filter(cli.filterDestinations, searcher.ruleMap[region][account]))
            searcher.ruleMap[region][account] = list(filter(cli.filterPorts, searcher.ruleMap[region][account]))
            searcher.ruleMap[region][account] = list(filter(cli.filterProtocols, searcher.ruleMap[region][account]))

    print('After Filtering')
    for region in searcher.ruleMap:
        for account in searcher.ruleMap[region]:
            print("{} account {}: {} rules".format(region, account, len(searcher.ruleMap[region][account])))



