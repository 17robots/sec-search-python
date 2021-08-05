import boto3
from .sso import SSO
from cli.cli import CLI
from aws.sec_group_rules import grab_sec_group_rules
from aws.instances import grab_instances
from threading import Thread, Event
import queue
import common.event
from .searchEnum import SearchFilters
from time import sleep
from datetime import datetime, timedelta
from .records import LogEntry
from itertools import chain

# TODO: Set up file output


class AWS:
    def __init__(self) -> None:
        self.currentRegion = ''
        self.ruleMap = {}
        self.groupMap = {}
        self.instanceMap = {}

    def search(self, cli: CLI, msgPmp: queue.Queue):
        sso = SSO()
        threads = []
        regions = list(filter(cli.filterRegions, sso.getRegions()))
        for region in regions:
            self.currentRegion = region
            if not region in self.ruleMap:
                self.ruleMap[region] = {}
                self.groupMap[region] = {}
                self.instanceMap[region] = {}

            accounts = list(
                filter(cli.filterAccounts, sso.getAccounts()['accountList']))
            msgPmp.put(common.event.InitEvent(
                reg=region, regionTotal=len(regions), counterTotal=len(accounts)), block=False)
            for account in accounts:
                self.currentAccount = account['accountId']
                if not account['accountId'] in self.ruleMap[region]:
                    self.ruleMap[region][account['accountId']] = []
                    self.groupMap[region][account['accountId']] = []
                    self.instanceMap[region][account['accountId']] = []

                def thread_func(region, account):
                    try:
                        reg = region
                        acct = account['accountId']
                        msgPmp.put(common.event.AccountStartedEvent(
                            reg=reg, acctId=acct), block=False)
                        creds = sso.getCreds(account=account)
                        ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                                  aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                        self.instanceMap[reg][acct] = grab_instances(
                            ec2_client)

                        self.ruleMap[reg][acct] = grab_sec_group_rules(
                            ec2_client)
                        self.ruleMap[reg][acct] = list(
                            filter(cli.filterPorts, self.ruleMap[reg][acct]))
                        self.ruleMap[reg][acct] = list(
                            filter(cli.filterProtocols, self.ruleMap[reg][acct]))
                        if cli.destString is not None or cli.sourceString is not None:
                            expand = cli.ExpandRule(
                                self.instanceMap[reg][acct])

                            expanded = list(
                                chain.from_iterable(map(expand, self.ruleMap[reg][acct])))

                            expanded = list(
                                filter(cli.filterSources, expanded))
                            expanded = list(
                                filter(cli.filterDestinations, expanded))

                            # grab the ruleids while removing duplicates
                            expanded = list(set(
                                [item.ruleId for item in expanded]))

                            # trim the rules to match
                            self.ruleMap[reg][acct] = list(
                                filter(lambda x: x['id'] in expanded, self.ruleMap[reg][acct]))

                        msgPmp.put(common.event.AccounFinishedEvent(
                            reg=reg, resTotal=len(self.ruleMap[reg][acct]), results=self.ruleMap[reg][acct]), block=False)
                    except Exception as e:
                        msgPmp.put(common.event.ErrorEvent(e=e))

                x = Thread(daemon=True, target=thread_func, name="{}-{}".format(
                    region, account['accountId']), args=(region, account))
                threads.append(x)
                x.start()

        for process in threads:
            process.join()

    def watch(self, cli: CLI, msgPmp: queue.Queue, killEvent: Event):
        sso = SSO()
        threads = []
        regions = list(filter(cli.filterRegions, sso.getRegions()))

        for region in regions:
            msgPmp.put(common.event.InitEvent(
                reg=region, regionTotal=len(regions), counterTotal=0), block=False)
            accounts = list(
                filter(cli.filterAccounts, sso.getAccounts()['accountList']))
            for account in accounts:
                try:
                    creds = sso.getCreds(account=account)
                    client = boto3.client('logs', region_name=region, aws_access_key_id=creds.access_key,
                                          aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                    paginator = client.get_paginator(
                        'describe_log_groups').paginate().search(SearchFilters.logs.value)

                    names = list(filter(lambda x: ('vpc' in x or 'VPC' in x) and 'tf' not in x,
                                        [val for val in paginator]))
                    msgPmp.put(common.event.AddLogStream(
                        region=region, amt=len(names)))

                    def sub_thread_func(name):
                        while not killEvent.is_set():
                            timestamp = int(
                                (datetime.now() - timedelta(minutes=1)).timestamp())
                            endstamp = int(
                                (datetime.now() + timedelta(minutes=5)).timestamp())
                            try:
                                paginator = client.get_paginator('filter_log_events').paginate(
                                    logGroupName=name,
                                    startTime=timestamp * 1000,
                                    endTime=endstamp * 1000,
                                    filterPattern="?ACCEPT ?REJECT",
                                    PaginationConfig={
                                        'PageSize': 1
                                    }
                                ).search(SearchFilters.events.value)
                                val = next(paginator, None)
                                while val is not None:
                                    if killEvent.is_set():
                                        return
                                    entry = LogEntry(
                                        val['timestamp'], val['message'])
                                    if cli.allowEntry(entry=entry):
                                        msgPmp.put(
                                            common.event.LogEntryReceivedEvent(
                                                log="[{}]{} {} {} {} {} {}[/{}]".format("green" if entry.action == "ACCEPT" else "red", entry.pkt_srcaddr, entry.pkt_dstaddr, entry.srcport, entry.dstport, entry.action, entry.flow_direction, "green" if entry.action == "ACCEPT" else "red"))
                                        )
                                    else:
                                        common.event.LogEntryReceivedEvent(
                                            log="Log Failed Filter"
                                        )
                                    val = next(paginator, None)
                                    sleep(.5)
                            except Exception as e:
                                common.event.ErrorEvent(
                                    e=e
                                )
                                break

                        msgPmp.put(
                            common.event.LogStreamStopped(region=region))
                        return

                    for name in names:
                        x = Thread(target=sub_thread_func, args=(name,))
                        threads.append(x)
                        msgPmp.put(
                            common.event.LogStreamStarted(region=region))
                        x.start()

                except Exception as e:
                    msgPmp.put(
                        common.event.ErrorEvent(e=e))
        for process in threads:
            process.join()
