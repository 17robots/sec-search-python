from .searchEnum import SearchFilters


def grab_sec_groups(client):
    groups = []
    paginator = client.get_paginator('describe_security_groups').paginate(
        PaginationConfig={'PageSize': 1000}).search(SearchFilters.groups.value)
    for val in paginator:
        groups.append(val)
    return groups
