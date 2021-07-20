import boto3
import json
from pathlib import Path
import os
from botocore.exceptions import ClientError


def grab_sec_groups():
    ec2 = boto3.client('ec2', region_name="us-west-2")
    ec2_regions = [region['RegionName']
                   for region in ec2.describe_regions()['Regions']]

    for region in ec2_regions:
        user_profile_directory = Path(os.getenv('USERPROFILE'))
        sso_cache_directory = user_profile_directory / '.aws' / 'sso' / 'cache'
        sso_cache_files = sso_cache_directory.glob('*.json')
        sso_cache_file = max(sso_cache_files, key=lambda x: x.stat().st_mtime)

        access_token = json.loads(sso_cache_file.read_text())['accessToken']

        sso_client = boto3.client('sso', region_name=region)

        accounts = sso_client.list_accounts(accessToken=access_token)

        for account in accounts['accountList']:
            print('Getting account roles for {}'.format(account['accountId']))

            print('Checking for AWSPowerUserAccess role')
            try:
                print('Getting AWSPowerUserAccess credentials for {}'.format(
                    account['accountId']))
                credentials = sso_client.get_role_credentials(
                    accountId=account['accountId'], accessToken=access_token, roleName='AWSPowerUserAccess')
            except ClientError as e:
                print(account['accountId'], e)
                continue

            session = boto3.Session(region_name='us-east-1', aws_access_key_id=credentials['roleCredentials']['accessKeyId'],
                                    aws_secret_access_key=credentials['roleCredentials']['secretAccessKey'], aws_session_token=credentials['roleCredentials']['sessionToken'])
            ec2_client = session.client('ec2')
            instances = ec2_client.describe_security_group_rules(
                MaxResults=1000)
            print(instances)
