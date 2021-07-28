from aws.aws import AWS
from aws.sso import SSO
from cli.common import command_arguments
from cli.cli import CLI
import boto3
from aws.searchEnum import SearchFilters
from time import sleep
import threading


@command_arguments
def watch(sources, regions, dests, display, accounts, ports, protocols, output, query):
    cli = CLI(subcommand="search", sources=sources, regions=regions, dests=dests,
              protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
    sso = SSO()

    account = sso.getAccounts()['accountList'][8]
    creds = sso.getCreds(account=account)
    log_client = boto3.client('logs', region_name="us-west-2", aws_access_key_id=creds.access_key,
                              aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)

    # grab log group names
    paginator = log_client.get_paginator(
        'describe_log_groups').paginate().search(SearchFilters.logs.value)

    names = list(filter(lambda x: ('vpc' in x or 'VPC' in x) and 'tf' not in x,
                        [val for val in paginator]))
    print(names)
    threads = []

    def thread_func(name):
        paginator = log_client.get_paginator('filter_log_events').paginate(
            logGroupName=name,
            startTime=1627482128000,
            filterPattern="?ACCEPT ?REJECT",
            PaginationConfig={
                'PageSize': 1
            },
        ).search(SearchFilters.events.value)
        count = 0
        try:
            while count < 5:
                print(next(paginator))
                sleep(1)
                count += 1

        except StopIteration as e:
            pass
    for name in names:
        x = threading.Thread(target=thread_func, args=(name,))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()
