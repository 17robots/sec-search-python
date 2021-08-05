from dataclasses import dataclass
from datetime import datetime
import ipaddress
from aws.records import LogEntry
from .lex import lex


@dataclass
class Rule:
    source: str
    dest: str
    ruleId: str


class CLI:
    def __init__(self, subcommand, sources, regions, dests, accounts, ports, protocols, cloudquery, output) -> None:
        self.subcommand = subcommand
        self.sourceString = sources
        self.sources = [source.strip(' ') for source in self.sourceString.split(
            ',')] if sources != None else []
        self.destString = dests
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
        if self.cloudQuery is not None:
            filters = lex(self.cloudQuery)
            for filter in filters:
                if 'port' in filter:
                    self.portString = ""
                    if len(self.ports) > 0:
                        for port in filters[filter]:
                            self.ports.append(port)
                            self.portString += "{},".format(port)
                    else:
                        self.ports = filters[filter]
                    self.ports = filters[filter]
                elif 'src' in filter or 'source' in filter:
                    self.sources = filters[filter]
                elif 'dst' in filter or 'dest' in filter or 'destination' in filter:
                    self.dests = filters[filter]
                elif 'protocol' in filter:
                    self.protocols = filter[filters]

    def filterAccounts(self, acct):
        if len(self.accounts) > 0:
            return acct['accountId'] in self.accounts
        return True  # if there are no accounts to filter by let all accts go through

    def filterRegions(self, region):
        if len(self.regions) > 0:
            return region in self.regions
        return True

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
        instanceCache = {}

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
                            source=selfIp if rule['isEgress'] else ip, dest=ip if rule['isEgress'] else selfIp, ruleId=rule['id']))
            else:
                if rule['cidrv4'] is not None:
                    for selfIp in myIps:
                        rules.append(Rule(
                            source=selfIp if rule['isEgress'] else rule['cidrv4'], dest=rule['cidrv4'] if rule['isEgress'] else selfIp, ruleId=rule['id']))
                else:
                    for selfIp in myIps:
                        rules.append(Rule(
                            source=selfIp if rule['isEgress'] else rule['cidrv6'], dest=rule['cidrv6'] if rule['isEgress'] else selfIp, ruleId=rule['id']))
            return rules
        return innerExpand

    def filterEntrySource(self, entry: LogEntry):
        if len(self.sources) > 0:
            for source in self.sources:
                try:
                    # x = ipaddress.ip_network(source)
                    # y = ipaddress.ip_network(entry.pkt_source)
                    # if x.subnet_of(y):
                    #     return True
                    # if y.subnet_of(x):
                    #     return True
                    if source in entry.pkt_source:
                        return True
                    if entry.pkt_source in source:
                        return True
                    return False
                except Exception as e:
                    continue
        return True

    def filterEntryDest(self, entry: LogEntry):
        for dest in self.dests:
            try:
                # x = ipaddress.ip_network(dest)
                # y = ipaddress.ip_network(entry.pkt_source)
                # if x.subnet_of(y):
                #     return True
                # if y.subnet_of(x):
                #     return True
                if dest in entry.pkt_dest:
                    return True
                if entry.pkt_dest in dest:
                    return True
                return False
            except Exception as e:
                continue
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

    def allowEntry(self, entry):
        if not self.filterEntryPorts(entry):
            return False
        if not self.filterEntryProtocol(entry):
            return False
        if not self.filterEntrySource(entry):
            return False
        if not self.filterEntryDest(entry):
            return False
        return True
