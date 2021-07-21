import boto3
from .sso import SSO
from .searchEnum import SearchFilters


def grab_sec_group_rules():
    sso = SSO()
    ruleMap = {}
    regions = ['us-west-2', 'us-east-1', 'eu-west-2', 'ap-northeast-1']
    regions = sso.getRegions()
    for region in regions:
        if not region in ruleMap:
            ruleMap[region] = {}
        for account in sso.getAccounts()['accountList']:
            if not account['accountId'] in ruleMap[region]:
                ruleMap[region][account['accountId']] = []

            creds = sso.getCreds(account=account)
            ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                      aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
            paginator = ec2_client.get_paginator(
                'describe_security_group_rules').paginate(PaginationConfig={'PageSize': 1000}).search(SearchFilters.rules.value)
            for val in paginator:
                for res in val:
                    ruleMap[region][account['accountId']].append(res)
    return ruleMap
