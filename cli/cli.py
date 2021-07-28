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

    def buildCloudQuery(self):
        return
        """
        parse @message /(?<version>\S+)\s+(?<account_id>\S+)\s+(?<interface_id>\S+)\s+(?<srcaddr>\S+)\s+(?<dstaddr>\S+)\s+(?<srcport>\S+)\s+(?<dstport>\S+)\s+(?<protocol>\S+)\s+(?<packets>\S+)\s+(?<bytes>\S+)\s+(?<start>\S+)\s+(?<end>\S+)\s+(?<action>\S+)\s+(?<log_status>\S+)(?:\s+(?<vpc_id>\S+)\s+(?<subnet_id>\S+)\s+(?<instance_id>\S+)\s+(?<tcp_flags>\S+)\s+(?<type>\S+)\s+(?<pkt_srcaddr>\S+)\s+(?<pkt_dstaddr>\S+))?(?:\s+(?<region>\S+)\s+(?<az_id>\S+)\s+(?<sublocation_type>\S+)\s+(?<sublocation_id>\S+))?(?:\s+(?<pkt_src_aws_service>\S+)\s+(?<pkt_dst_aws_service>\S+)\s+(?<flow_direction>\S+)\s+(?<traffic_path>\S+))?/
        | filter pkt_srcaddr="192.0.2.1" and pkt_dstaddr="198.51.100.1"
        | display action, @timestamp, pkt_srcaddr, srcport, pkt_dstaddr, dstport, protocol, vpc_id, subnet_id, instance_id
        """
