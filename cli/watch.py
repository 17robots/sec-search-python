from cli.common import command_arguments, programLoop


@command_arguments
def watch(sources, dests, display, protocols, accounts, ports, output):
    programLoop('watch', sources, dests, display,
                protocols, accounts, ports, output)
