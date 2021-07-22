import boto3
from .sso import SSO
from .searchEnum import SearchFilters


def grab_sec_group_rules(client):
    rules = []
    paginator = client.get_paginator('describe_security_group_rules').paginate(PaginationConfig={'PageSize': 1000}).search(SearchFilters.rules.value)
    for val in paginator:
        # print(val)
        rules.append(val)
    return rules
