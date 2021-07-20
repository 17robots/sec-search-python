from abc import abstractclassmethod
from botocore.exceptions import ClientError
from pathlib import Path
import boto3
import boto3.session
import json
import os


def getCreds(client, account, token):
    try:
        print('Getting AWSPowerUserAccess credentials for {}'.format(
            account['accountId']))
        return client.get_role_credentials(
            accountId=account['accountId'], accessToken=token, roleName='AWSPowerUserAccess')
    except ClientError as e:
        print(account['accountId'], e)
