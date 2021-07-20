import boto3
from aws.sso import SSO


def grab_instances():
    sso = SSO()
    regions = ['us-west-2', 'us-east-1', 'eu-west-2', 'ap-northeast-1']
    regions = sso.getRegions()
    for region in regions:
        print(region)
        for account in sso.getAccounts()['accountList']:
            creds = sso.getCreds(account=account)
            ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds.access_key,
                                      aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
            instances = ec2_client.describe_instances()
            print(instances)
