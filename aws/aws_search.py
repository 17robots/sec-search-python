import boto3
from .sso import SSO
from cli.cli import CLI
from aws.sec_group_rules import grab_sec_group_rules
from aws.sec_groups import grab_sec_groups
from aws.instances import grab_instances
from threading import Thread
import queue
import common.event


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
                reg=region, regionTotal=len(regions), acctTotal=len(accounts)), block=False)
            for account in accounts:
                self.currentAccount = account['accountId']
                if not account['accountId'] in self.ruleMap[region]:
                    self.ruleMap[region][account['accountId']] = []
                    self.groupMap[region][account['accountId']] = []
                    self.instanceMap[region][account['accountId']] = []

                def thread_func(region, account):
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
                    self.ruleMap[reg][acct] = list(
                        filter(cli.filterSources, self.ruleMap[reg][acct]))
                    self.ruleMap[reg][acct] = list(
                        filter(cli.filterDestinations, self.ruleMap[reg][acct]))

                    # expand = cli.ExpandRule(self.instanceMap[reg][acct])

                    # expanded = list(map(expand, self.ruleMap[reg][acct]))

                    # for ruleArr in expanded:
                    #     print(ruleArr)

                    msgPmp.put(common.event.AccounFinishedEvent(
                        reg=reg, resTotal=len(self.ruleMap[reg][acct]), results=self.ruleMap[reg][acct]), block=False)

                x = Thread(daemon=True, target=thread_func, name="{}-{}".format(
                    region, account['accountId']), args=(region, account))
                threads.append(x)
                x.start()

        for process in threads:
            process.join()
