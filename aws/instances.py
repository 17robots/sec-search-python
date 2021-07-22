from .searchEnum import SearchFilters


def grab_instances(client):
    instances = []
    paginator = client.get_paginator('describe_instances').paginate().search(SearchFilters.instances.value)
    for val in paginator:
        for res in val:
            # print(res)
            instances.append(res)
    return instances
