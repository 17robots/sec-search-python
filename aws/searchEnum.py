from enum import Enum


class SearchFilters(Enum):
    instances = "Reservations[*].Instances[*].{id:InstanceId, privdns:PrivateDnsName, pubdns:PublicDnsName, pubip:PublicIpAddress, vpi:VpiId, privaddresses:NetworkInterfaces[*].{ipv6s:Ipv6Addresses[*], ips:PrivateIpAddresses[*].PrivateIpAddress}}"
    groups = "SecurityGroups[*].{id:GroupId, name:GroupName, description:Description, vpc:VpcId}"
    rules = "SecurityGroupRules[*].{id:SecurityGroupRuleId, description:Description, groupId:GroupId, isEgress:IsEgress, protocol:IpProtocol, from:FromPort, to:ToPort, cidrv4:CidrIpv4, cidrv6:CidrIpv6, prefixId:PrefixListId}"
