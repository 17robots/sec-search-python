class CLI:
    def __init__(self, subcommand, sources, regions, dests, accounts, ports, protocols, cloudquery, output) -> None:
        self.subcommand = subcommand
        self.sourceString = sources
        self.sources = [source.split(' ')
                        for source in self.sourceString.split(',')] if sources != None else []
        self.destString = dests
        self.dests = [dest.split(' ')
                      for dest in self.destString.split(',')] if dests != None else []
        self.accountString = accounts
        self.accounts = [acct.split(' ')
                         for acct in self.accountString.split(',')] if accounts != None else []
        self.portString = ports
        self.ports = [port.split(' ')
                      for port in self.portString.split(',')] if ports != None else []
        self.protocolString = protocols
        self.protocols = [protocol.split(' ')
                          for protocol in self.protocolString.split(',')] if protocols != None else []
        self.regionString = regions
        self.regions = [region.split(' ')
                        for region in self.regionString.split(',')] if regions != None else []
        self.query = cloudquery,
        self.outputFile = output

    def filterAccounts(self, acct):
        if len(self.accounts) > 0:
            return acct in self.accounts
        return True  # if there are no accounts to filter by let all accts go through

    def filterRegions(self, region):
        if len(self.regions) > 0:
            return region in self.regions
        return True

    def filterSources(self, source):
        if len(self.sources) > 0:
            return source in self.sources
        return True

    def filterDestinations(self, dest):
        if len(self.dests) > 0:
            return dest in self.dests
        return True

    def filterPorts(self, port):
        if len(self.ports) > 0:
            return port in self.ports
        return True

    def filterProtocols(self, protocol):
        if len(self.protocol) > 0:
            return protocol in self.protocol
        return True
