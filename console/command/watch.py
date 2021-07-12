from console.command.common import parseArr, command_arguments

@command_arguments
def watchCommand(source, dest, fields, accounts, ports):
    parsedAccts = []
    parsedFields = []
    if accounts != None:
        parsedAccts = parseArr(accounts)
    if fields != None:
        parsedFields = parseArr(fields)
    if ports != None:
        parsedFields = parseArr(ports)

    print("Watching with params {}, {}, {}, {}, {}".format(source, dest, parsedFields, parsedAccts, ports))
