from cli.common import command_arguments, programLoop


@command_arguments
def watch(sources, regions, dests, display, accounts, ports, protocols, output, query):
    programLoop('watch', sources, dests, display,
                protocols, accounts, ports, output)
