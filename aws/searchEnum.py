from enum import Enum


class SearchFilters(Enum):
    instances = "Reservations[*].Instances[*].{id:InstanceId, privdns:PrivateDnsName, pubdns:PublicDnsName, secgrps:SecurityGroups[*].GroupId, othergrps:NetworkInterfaces[*].Groups[*].GroupId, pubip:PublicIpAddress, vpcId:VpiId, privaddresses:NetworkInterfaces[*].{ipv6s:Ipv6Addresses[*], ips:PrivateIpAddresses[*].PrivateIpAddress}}"
    groups = "SecurityGroups[*].{id:GroupId, name:GroupName, description:Description, vpc:VpcId, inbound:IpPermissions[*].{ips:IpRanges[*].{ip:CidrIp}, ipv6s:Ipv6Ranges[*].{ip:CidrIpv6}, from:FromPort, to:ToPort, protocol:IpProtocol}, outbound:IpPermissionsEgress[*].{ips:IpRanges[*].{ip:CidrIp}, ipv6s:Ipv6Ranges[*].{ip:CidrIpv6}, from:FromPort, to:ToPort, protocol:IpProtocol}}"
    rules = "SecurityGroupRules[*].{id:SecurityGroupRuleId, description:Description, groupId:GroupId, isEgress:IsEgress, protocol:IpProtocol, from:FromPort, to:ToPort, cidrv4:CidrIpv4, cidrv6:CidrIpv6, referencedGroup:ReferencedGroupInfo.GroupId}"
