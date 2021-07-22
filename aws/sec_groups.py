from .searchEnum import SearchFilters


def grab_sec_groups(client):
    groups = []
    paginator = client.get_paginator('describe_security_groups').paginate().search(SearchFilters.groups.value)
    for val in paginator:
        # print(val)
        groups.append(val)
    return groups
