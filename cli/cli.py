from dataclasses import dataclass
import ipaddress
from aws.records import LogEntry
from aws.protocols import intToProtocolTable, protocolToIntTable


@dataclass
class Rule:
    source: str
    dest: str
    ruleId: str


class CLI:
    def __init__(self, subcommand, sources, regions, dests, accounts, ports, protocols, cloudquery, output) -> None:
        self.subcommand = subcommand
        self.sourceString = sources
        if self.sourceString is not None and '@' in self.sourceString:
            self.sources = []
            try:
                with open(self.sourceString[1:], 'r') as f:
                    for line in f:
                        self.sources.append(line.strip())
            except Exception as e:
                raise Exception(f"Invalid Filename {self.sourceString[1:]}")
        else:
            self.sources = [source.strip(' ') for source in self.sourceString.split(
                ',')] if sources != None else []
        self.destString = dests
        if self.destString is not None and '@' in self.destString:
            self.dests = []
            try:
                with open(self.destString[1:], 'r') as f:
                    for line in f:
                        self.dests.append(line.strip())
            except Exception as e:
                raise Exception(f"Invalid Filename {self.destString[1:]}")

        else:
            self.dests = [dest.strip(' ') for dest in self.destString.split(
                ',')] if dests != None else []
        self.accountString = accounts
        self.accounts = [acct.strip(' ') for acct in self.accountString.split(
            ',')] if accounts != None else []
        self.portString = ports
        self.ports = [int(port.strip(' ')) for port in self.portString.split(
            ',')] if ports != None else []
        self.protocolString = protocols
        self.protocols = [protocol.strip(' ') for protocol in self.protocolString.split(
            ',')] if protocols != None else []
        self.regionString = regions
        self.regions = [region.strip(' ') for region in self.regionString.split(
            ',')] if regions != None else []
        self.outputFile = output
        self.cloudQuery = cloudquery

    def filterAccounts(self, acct):
        if len(self.accounts) > 0:
            return acct['accountId'] in self.accounts
        return True  # if there are no accounts to filter by let all accts go through

    def filterRegions(self, region):
        if len(self.regions) > 0:
            return region in self.regions
        return True

    def buildFilters(self):
        if self.cloudQuery is not None:
            return self.cloudQuery
        returnString = ""
        if len(self.sources) > 0:
            returnString += "filter ("
            for source in self.sources:
                returnString += f"pkt_srcaddr = {source} or "
            returnString.rsplit(' or ')
            returnString += ')'
        if len(self.dests) > 0:
            returnString += " and (" if returnString != "" else " | filter ("
            for dest in self.dests:
                returnString += f"pkt_dstaddr = {dest} or "
            returnString.rsplit(' or ')
            returnString += ')'
        if len(self.ports) > 0:
            returnString += " and (" if returnString != "" else " | filter ("
            for port in self.ports:
                returnString += f"srcport = {port} or "
            returnString.rsplit(' or ')
            returnString += ')'
            returnString += " and (" if returnString != "" else " | filter ("
            for port in self.ports:
                returnString += f"dstport = {port} or "
            returnString.rsplit(' or ')
            returnString += ')'
        if len(self.protocols) > 0:
            returnString += " and (" if returnString != "" else " | filter ("
            for protocol in self.protocols:
                returnString += f"protocol = {protocol if protocol.isnumeric() else protocolToIntTable[protocol]} or "
            returnString.rsplit(' or ')
            returnString += ')'
        return returnString

    def filterSources(self, expandedRule: Rule):
        if len(self.sources) > 0:
            for source in self.sources:
                try:
                    x = ipaddress.ip_network(source)
                    y = ipaddress.ip_network(expandedRule.source)
                    if x.subnet_of(y):
                        return True
                    if y.subnet_of(x):
                        return True
                    if source in expandedRule.source:

                        return True
                    if expandedRule.source in source:

                        return True
                    return False
                except Exception as e:
                    continue
        return True

    def filterDestinations(self, expandedRule: Rule):
        if len(self.dests) > 0:
            for dest in self.dests:
                try:
                    x = ipaddress.ip_network(dest)
                    y = ipaddress.ip_network(expandedRule.dest)
                    if x.subnet_of(y):
                        return True
                    if y.subnet_of(x):
                        return True
                    if dest in expandedRule.dest:
                        return True
                    if expandedRule.dest in dest:
                        return True
                    return False
                except Exception as e:
                    continue
        return True

    def filterPorts(self, rule):
        if len(self.ports) > 0:
            for port in self.ports:
                if port == rule['from']:
                    return True
                if port == rule['to']:
                    return True
            return False
        return True

    def filterProtocols(self, rule):
        if len(self.protocols) > 0:
            for protocol in self.protocols:
                if protocol in rule['protocol']:
                    return True
            return False
        return True

    def ExpandRule(self, instances):
        def traceGroup(group):
            ipaddresses = []
            for instance in instances:
                if 'secgrps' in instance:
                    if group in instance['secgrps']:
                        for ipaddr in instance['privaddresses']:
                            for ip in ipaddr['ips']:
                                ipaddresses.append(ip)
                if 'othergrps' in instance:
                    if group in instance['othergrps']:
                        for ipaddr in instance['privaddresses']:
                            for ip in ipaddr['ips']:
                                ipaddresses.append(ip)
            return ipaddresses

        def innerExpand(rule):
            rules = []
            myIps = traceGroup(rule['groupId'])
            if rule['referencedGroup'] is not None:
                secIps = traceGroup(rule['referencedGroup'])
                for selfIp in myIps:
                    for ip in secIps:

                        rules.append(Rule(
                            source=selfIp if rule['isEgress'] else ip, dest=ip if rule['isEgress'] else selfIp, ruleId=str(rule)))
            else:
                if rule['cidrv4'] is not None:
                    for selfIp in myIps:
                        rules.append(Rule(
                            source=selfIp if rule['isEgress'] else rule['cidrv4'], dest=rule['cidrv4'] if rule['isEgress'] else selfIp, ruleId=str(rule)))
                else:
                    for selfIp in myIps:
                        rules.append(Rule(
                            source=selfIp if rule['isEgress'] else rule['cidrv6'], dest=rule['cidrv6'] if rule['isEgress'] else selfIp, ruleId=str(rule)))
            return rules
        return innerExpand

    def filterEntrySource(self, entry: LogEntry):
        if len(self.sources) > 0:
            return entry.pkt_srcaddr in self.sources
        return True

    def filterEntryDest(self, entry: LogEntry):
        if len(self.dests) > 0:
            return entry.pkt_srcaddr in self.sources
        return True

    def filterEntryPorts(self, entry: LogEntry):
        if len(self.ports) > 0:
            for port in self.ports:
                if int(port) == (entry.dstport):
                    return True
                if int(port) == int(entry.srcport):
                    return True
            return False
        return True

    def filterEntryProtocol(self, entry: LogEntry):
        if len(self.protocols) > 0:
            for protocol in self.protocols:
                if protocol in entry.protocol:
                    return True
            return False
        return True

    def allowEntry(self, entry: LogEntry):
        if not self.filterEntryPorts(entry):
            return False
        if not self.filterEntryProtocol(entry):
            return False
        if not self.filterEntrySource(entry):
            return False
        if not self.filterEntryDest(entry):
            return False
        return True
