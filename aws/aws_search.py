import boto3
from .sso import SSO
from cli.cli import CLI
from aws.sec_group_rules import grab_sec_group_rules
from aws.sec_groups import grab_sec_groups
from aws.instances import grab_instances

class AWS:
    def __init__(self) -> None:
        self.currentRegion = ''
        self.ruleMap = {}
        self.groupMap = {}
        self.instanceMap = {}

    def search(self, cli: CLI):
        sso = SSO()
        regions = filter(cli.filterRegions,sso.getRegions())
        for region in regions:
            self.currentRegion = region
            if not region in self.ruleMap:
                self.ruleMap[region] = {}
                self.groupMap[region] = {}
                self.instanceMap[region] = {}
            accounts = sso.getAccounts()
            for account in filter(cli.filterAccounts,accounts['accountList']):
                self.currentAccount = account['accountId']
                if not account['accountId'] in self.ruleMap[region]:
                    self.ruleMap[region][account['accountId']] = []
                    self.groupMap[region][account['accountId']] = []
                    self.instanceMap[region][account['accountId']] = []
                creds = sso.getCreds(account=account)
                ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                        aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                
                # print("grabbing clients for region {} account {}".format(region, account['accountId']))
                self.instanceMap[region][account['accountId']] = grab_instances(ec2_client)
                
                # print("grabbing rules for region {} account {}".format(region, account['accountId']))
                self.ruleMap[region][account['accountId']] = grab_sec_group_rules(ec2_client)

                # print("grabbing groups for region {} account {}".format(region, account['accountId']))
                self.groupMap[region][account['accountId']] = grab_sec_groups(ec2_client)