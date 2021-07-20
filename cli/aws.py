import boto3.session
import click
import boto3
import json
import os
from botocore.exceptions import ClientError
from pathlib import Path


@click.command()
def aws():
    user_profile_directory = Path(os.getenv('USERPROFILE'))
    sso_cache_directory = user_profile_directory / '.aws' / 'sso' / 'cache'
    sso_cache_files = sso_cache_directory.glob('*.json')
    sso_cache_file = max(sso_cache_files, key=lambda x: x.stat().st_mtime)

    access_token = json.loads(sso_cache_file.read_text())['accessToken']

    sso_client = boto3.client('sso', region_name='us-east-1')

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

    session = boto3.Session(region_name='us-east-1', aws_access_key_id=credentials['roleCredentials']['accessKeyId'],
                            aws_secret_access_key=credentials['roleCredentials']['secretAccessKey'], aws_session_token=credentials['roleCredentials']['sessionToken'])

    ec2_client = session.client('ec2')
    instances = ec2_client.describe_instances()
