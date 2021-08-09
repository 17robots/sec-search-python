from logging import error
import boto3
from .sso import SSO
from cli.cli import CLI
from aws.sec_group_rules import grab_sec_group_rules
from aws.instances import grab_instances
from threading import Thread, Event
import threading
import queue
import common.event
from .searchEnum import SearchFilters
from datetime import datetime, timedelta
from itertools import chain
from .records import LogEntry
import time
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename='mainLog.txt')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(thread)d %(threadName)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

message_pattern = '/(?<version>\S+)\s+(?<account_id>\S+)\s+(?<interface_id>\S+)\s+(?<srcaddr>\S+)\s+(?<dstaddr>\S+)\s+(?<srcport>\S+)\s+(?<dstport>\S+)\s+(?<protocol>\S+)\s+(?<packets>\S+)\s+(?<bytes>\S+)\s+(?<start>\S+)\s+(?<end>\S+)\s+(?<action>\S+)\s+(?<log_status>\S+)(?:\s+(?<vpc_id>\S+)\s+(?<subnet_id>\S+)\s+(?<instance_id>\S+)\s+(?<tcp_flags>\S+)\s+(?<type>\S+)\s+(?<pkt_srcaddr>\S+)\s+(?<pkt_dstaddr>\S+))?(?:\s+(?<region>\S+)\s+(?<az_id>\S+)\s+(?<sublocation_type>\S+)\s+(?<sublocation_id>\S+))?(?:\s+(?<pkt_src_aws_service>\S+)\s+(?<pkt_dst_aws_service>\S+)\s+(?<flow_direction>\S+)\s+(?<traffic_path>\S+))?/'

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
                    logger.debug(f"Account {account['accountId']}\n")
                    creds = sso.getCreds(account=account)
                    client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                          aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                    paginator = client.get_paginator(
                        'describe_flow_logs').paginate().search(SearchFilters.logs.value)

                    names = [val for val in paginator]
                    msgPmp.put(common.event.AddLogStream(
                        region=region, amt=len(names)))

                    clientLock = threading.Lock()

                    def sub_thread_func(name):
                        results = []
                        myAccount = account
                        nonlocal clientLock
                        logger.debug(f"Trying Log: {name}\n")

                        start_time = None
                        while not killEvent.is_set():
                            try:
                                haveResults = False
                                with clientLock:
                                    creds = sso.getCreds(account=myAccount)
                                    threadClient = boto3.client('logs', region_name=region, aws_access_key_id=creds.access_key,
                                            aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                                fullQuery = f"fields @timestamp, @message | parse @message {message_pattern} {cli.buildFilters()}"

                                if start_time:
                                    if haveResults:
                                        start_time = end_time;
                                        end_time = datetime.now()
                                        haveResults = False
                                else:
                                    end_time = datetime.now()
                                    start_time = end_time - timedelta(minutes=5)

                                query_id = threadClient.start_query(logGroupName=name, startTime=int(start_time.timestamp()), endTime=int(
                                    end_time.timestamp()), queryString=fullQuery)['queryId']
                                logger.debug(f"{account['accountId']}: {query_id}")
                                while True:
                                    response = threadClient.get_query_results(
                                        queryId=query_id)
                                    if response['results']:
                                        haveResults = True
                                    for result in response['results']:
                                        logger.debug(' '.join([val['value']
                                                        for val in result]))
                                        msgPmp.put(common.event.LogEntryReceivedEvent(
                                            log=' '.join([val['value']
                                                        for val in result])
                                        ))
                                        
                                    if response['status'] == 'Complete':
                                        break
                            except Exception as e:
                                common.event.ErrorEvent(e=e)
                                logger.error(f"We Encountered An Error: {str(e)}\n")
                                break
                        msgPmp.put(
                            common.event.LogStreamStopped(region=region))
                        return

                    for name in names:
                        x = Thread(target=sub_thread_func, args=(name,), name=f"{region}-{account['accountId']}-{name}")
                        threads.append(x)
                        msgPmp.put(
                            common.event.LogStreamStarted(region=region))
                        x.start()

                except Exception as e:
                    msgPmp.put(
                        common.event.ErrorEvent(e=e))
        for process in threads:
            process.join()
