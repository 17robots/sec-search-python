import boto3
from aws.sso import SSO
from .searchEnum import SearchFilters


def grab_sec_groups():
    sso = SSO()
    groupMap = {}
    regions = ['us-west-2', 'us-east-1', 'eu-west-2', 'ap-northeast-1']
    regions = sso.getRegions()
    for region in regions:
        if not region in groupMap:
            groupMap[region] = {}
        for account in sso.getAccounts()['accountList']:
            if not account['accountId'] in groupMap[region]:
                groupMap[region][account['accountId']] = []
            creds = sso.getCreds(account=account)
            ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                      aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
            paginator = ec2_client.get_paginator(
                'describe_security_groups').paginate().search(SearchFilters.groups.value)
            for val in paginator:
                for res in val:
                    groupMap[region][account['accountId']].append(res)
    return groupMap
