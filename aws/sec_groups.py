import boto3
from aws.sso import SSO

def grab_sec_groups():
    sso = SSO()
    initAccount = sso.getAccounts()['accountList'][0]
    initCreds = sso.getCreds(initAccount)
    initSession = boto3.Session(region_name='us-east-1', aws_access_key_id=initCreds['roleCredentials']['accessKeyId'], aws_secret_access_key=initCreds['roleCredentials']['secretAccessKey'], aws_session_token=initCreds['roleCredentials']['sessionToken'])
    ec2 = initSession.client('ec2')
    ec2_regions = [region['RegionName']
                   for region in ec2.describe_regions()['Regions']]
    for region in ec2_regions:
        for account in sso.getAccounts()['accountList']:
            creds = sso.getCreds(account=account)
            ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=creds['roleCredentials']['accessKeyId'], aws_secret_access_key=creds['roleCredentials']['secretAccessKey'], aws_session_token=creds['roleCredentials']['sessionToken'])
            instances = ec2_client.describe_instances()
            print(instances)
