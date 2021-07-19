from cli.common import command_arguments, programLoop


@command_arguments
def search(sources, dests, display, protocols, accounts, ports, output):
    programLoop('search', sources, dests, display,
                protocols, accounts, ports, output)
