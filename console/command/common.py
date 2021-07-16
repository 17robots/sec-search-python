import click


def parseArr(arr: str):
    newList = arr.split(',')
    returnedArr = []
    for item in newList:
        returnedArr.append(item.strip(' '))
    return returnedArr

# decorator to keep command options similar across


def command_arguments(func):
    @click.command()
    @click.option('-source', default=None, type=str, help='Name or ip of source vm', required=False)
    @click.option('-dest',  default=None, type=str, help='Name or ip of dest vm', required=False)
    @click.option('-fields',  default=None, type=str, help='AWS fields to show on output', required=False)
    @click.option('-accounts',  default=None, type=str, help='AWS accounts within user credentials to filter by', required=False)
    @click.option('-ports',  default=None, type=str, help='Ports to filter by', required=False)
    @click.option('-output', default=None, type=str, help="File to output results of command to")
    def wrapped_func(*args, **kwargs):
        func(*args, **kwargs)
    return wrapped_func


def parseArrArgs(fields, accounts, ports):
    returnArgs = {}
    returnArgs.fieldList = parseArr(fields)
    returnArgs.accountList = parseArr(accounts)
    returnArgs.portList = parseArr(ports)
    return returnArgs
