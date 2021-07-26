from dataclasses import dataclass
import ipaddress
import re

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
        self.query = cloudquery,
        self.outputFile = output

    def filterAccounts(self, acct):
        if len(self.accounts) > 0:
            return acct['accountId'] in self.accounts
        return True  # if there are no accounts to filter by let all accts go through

    def filterRegions(self, region):
        if len(self.regions) > 0:
            return region in self.regions
        return True

    def filterSources(self, rule):
        if len(self.sources) > 0:
            for source in self.sources:
                if ipaddress.ip_address(source) in ipaddress.ip_network(rule['cidrv4']):
                    return True
                if source in rule['cidrv4']:
                    return True
                if ipaddress.ip_address(rule['cidrv4']) in ipaddress.ip_network(source):
                    return True
                return False
        return True

    def filterDestinations(self, rule):
        if len(self.dests) > 0:
            if rule['isEgress']:
                for dest in self.dests:
                    # check if the source is in the subnet
                    if ipaddress.ip_address(dest) in ipaddress.ip_network(rule['cidrv4']):
                        return True
                    # check if the source is the same network as the rule
                    if dest in rule['cidrv4']:
                        return True
                    # check if the source is the network of the rules ip
                    if ipaddress.ip_address(rule['cidrv4']) in ipaddress.ip_network(dest):
                        return True
                    return False
            return True
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
        def inner(rule):
            rules = []
            def walkGroup(group):
                pass
            if rule['referencedGroup'] is not None:
                # we have a referenced group, we need all of the ips on the instances that reference this group to make rules for them
                for instance in instances:
                    if 'secgrps' in instance:
                        if rule['referencedGroup'] in instance['secgrps']:
                            for ipaddr in instance['privaddresses']:
                                for ip in ipaddr['ips']:
                                    rules.append(Rule(source=None if rule['isEgress'] else ipaddr, dest=ipaddr if rule['isEgress'] else None, ruleId=rule['id']))
            else:
                if(rule['cidrv4'] is not None):
                    try:
                        x = ipaddress.ip_address(rule['cidrv4'])
                        for instance in instances:
                            for ip in instance['ips']:
                                rules.append(Rule(source=None if rule['isEgress'] else ip, dest=ip if rule['isEgress'] else None, ruleId=rule['id']))
                    except ValueError as e:
                        # we know the cidr provided isnt an ip but rather a network
                        rules.append(Rule(source=None if rule['isEgress'] else rule['cidrv4'], dest=rule['cidrv4'] if rule['isEgress'] else None, ruleId=rule['id']))
                else:
                    try:
                        x = ipaddress.ip_address(rule['cidrv6'])
                        for instance in instances:
                            for ip in instance['ipv6s']:
                                rules.append(Rule(source=None if rule['isEgress'] else ip, dest=ip if rule['isEgress'] else None, ruleId=rule['id']))
                    except ValueError as e:
                        # we know the cidr provided isnt an ip but rather a network
                        rules.append(Rule(source=None if rule['isEgress'] else rule['cidrv6'], dest=rule['cidrv6'] if rule['isEgress'] else None, ruleId=rule['id']))
            return rules
        return inner
