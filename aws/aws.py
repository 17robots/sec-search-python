from aws.groups import grab_sec_groups
from dataclasses import dataclass
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
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename='mainLog.txt')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(thread)d %(threadName)s %(levelname)s %(message)s')
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
                                # {cli.buildFilters()}
                                fullQuery = f"fields @timestamp, @message | parse @message {message_pattern} {cli.buildFilters()}"
                                logger.debug(f"Query: {fullQuery}")

                                if start_time:
                                    if haveResults:
                                        start_time = end_time
                                        end_time = datetime.now()
                                        haveResults = False
                                else:
                                    end_time = datetime.now()
                                    start_time = end_time - \
                                        timedelta(minutes=5)

                                query_id = threadClient.start_query(logGroupName=name, startTime=int(start_time.timestamp()), endTime=int(
                                    end_time.timestamp()), queryString=fullQuery)['queryId']
                                logger.debug(
                                    f"{account['accountId']}: {query_id}\n")
                                while True:
                                    response = threadClient.get_query_results(
                                        queryId=query_id)
                                    if response['results']:
                                        haveResults = True
                                    for result in response['results']:
                                        logger.debug(' '.join([val['value']
                                                               for val in result]))
                                        time.sleep(.5)
                                        msgPmp.put(common.event.LogEntryReceivedEvent(
                                            log=' '.join([val['value']
                                                          for val in result])
                                        ))

                                    if response['status'] == 'Complete':
                                        break
                            except Exception as e:
                                common.event.ErrorEvent(e=e)
                                logger.error(
                                    f"We Encountered An Error: {str(e)}\n")
                                break
                        msgPmp.put(
                            common.event.LogStreamStopped(region=region))
                        return

                    for name in names:
                        x = Thread(target=sub_thread_func, args=(
                            name,), name=f"{region}-{account['accountId']}-{name}")
                        threads.append(x)
                        msgPmp.put(
                            common.event.LogStreamStarted(region=region))
                        x.start()

                except Exception as e:
                    msgPmp.put(
                        common.event.ErrorEvent(e=e))
        for process in threads:
            process.join()

    def diff(self, cli: CLI, msgPmp: queue.Queue):
        sso = SSO()
        threads = []
        self.group1_diffs = []
        self.group2_diffs = []
        sg1, sg2 = None, None
        regions = sso.getRegions()
        for region in regions:
            accounts = sso.getAccounts()['accountList']
            for account in accounts:
                self.currentAccount = account['accountId']

                def thread_func(region, account):
                    try:
                        reg = region
                        acct = account
                        creds = sso.getCreds(account=acct)
                        client = boto3.client('ec2', region_name=reg, aws_access_key_id=creds.access_key,
                                              aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                        for group in grab_sec_groups(client):
                            if group['id'] == cli.group1:
                                nonlocal sg1
                                sg1 = group
                            elif group['id'] == cli.group2:
                                nonlocal sg2
                                sg2 = group
                    except Exception as e:
                        msgPmp.put(common.event.ErrorEvent(e=e))
                x = Thread(daemon=True, target=thread_func, name="{}-{}".format(
                    region, account['accountId']), args=(region, account))
                threads.append(x)
                x.start()

        for process in threads:
            process.join()

        if sg1 == None or sg2 == None:
            if sg1 == None:
                if sg2 == None:
                    msgPmp.put(common.event.LoadDiffsEvent(grp1_diffs=[
                               f'Unable to find {cli.group1}'], grp2_diffs=[f'Unable to find {cli.group2}']))
                else:
                    msgPmp.put(common.event.LoadDiffsEvent(grp1_diffs=[
                               f'Unable to find {cli.group1}'], grp2_diffs=[f'Refusing to load {cli.group2} because other group not found']))
                return
            if sg2 == None:
                msgPmp.put(common.event.LoadDiffsEvent(grp1_diffs=[f'Refusing to load {cli.group1} because other group not found'], grp2_diffs=[
                    f'Unable to find {cli.group2}']))
            return
        logger.debug(f"{sg1}\n{sg2}\n")
        logger.debug("Rule Similarities\n")
        logger.debug(f"{cli.group1}\n")
        for inbound_rule in sg1['inbound']:
            if not contains_rule(rules=sg2['inbound'], rule=inbound_rule):
                self.group1_diffs.append(inbound_rule)  # add a difference
            else:
                logger.debug(inbound_rule)

        for outbound_rule in sg1['outbound']:
            if not contains_rule(rules=sg2['outbound'], rule=outbound_rule):
                self.group1_diffs.append(outbound_rule)  # add a difference
            else:
                logger.debug(outbound_rule)

        logger.debug(f"{cli.group2}\n")
        for inbound_rule in sg2['inbound']:
            if not contains_rule(rules=sg1['inbound'], rule=inbound_rule):
                self.group2_diffs.append(inbound_rule)  # add a difference
            else:
                logger.debug(inbound_rule)

        for outbound_rule in sg2['outbound']:
            if not contains_rule(rules=sg1['outbound'], rule=outbound_rule):
                self.group2_diffs.append(outbound_rule)  # add a difference
            else:
                logger.debug(outbound_rule)

        msgPmp.put(common.event.LoadDiffsEvent(
            grp1_diffs=self.group1_diffs if len(self.group1_diffs) > 0 else [f'All rules present in {cli.group1}'], grp2_diffs=self.group2_diffs if len(self.group2_diffs) > 0 else [f'All rules present in {cli.group2}']))


def contains_rule(rule, rules):
    for inner_rule in rules:
        if equals(inner_rule, rule):
            return True
    return False


def contains_ip(ip, ips):
    for inner_ip in ips:
        if inner_ip['ip'] == ip:
            return True
    return False


def equals(rule1, rule2):
    if rule1['from'] != rule2['from']:
        return False
    if rule1['to'] != rule2['to']:
        return False
    if rule1['protocol'] != rule2['protocol']:
        return False
    for ip in rule1['ips']:
        if not contains_ip(ips=rule2['ips'], ip=ip['ip']):
            return False
    for ip in rule1['ipv6s']:
        if not contains_ip(ips=rule2['ipv6s'], ip=ip['ip']):
            return False
    return True
    # IpPermissions[*].{ips:IpRanges[*].{ip:CidrIp}, ipv6s:Ipv6Ranges[*].{ip:CidrIpv6}, from:FromPort, to:ToPort, protocol:IpProtocol}
