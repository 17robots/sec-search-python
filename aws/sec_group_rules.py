import boto3
from .sso import SSO


def grab_sec_group_rules():
    sso = SSO()
    regions = ['us-west-2', 'us-east-1', 'eu-west-2', 'ap-northeast-1']
    regions = sso.getRegions()
    for region in regions:
        print(region)
        for account in sso.getAccounts()['accountList']:
            creds = sso.getCreds(account=account)
            ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                      aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
            return ec2_client.describe_security_group_rules(
                MaxResults=1000)
