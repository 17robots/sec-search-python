from botocore.exceptions import ClientError
from pathlib import Path
import boto3
import boto3.session
import json
import os
from dataclasses import dataclass

class SSO:
    def __init__(self) -> None:
        self.region = 'us-east-1'
        user_profile_directory = Path(os.getenv('USERPROFILE'))
        sso_cache_directory = user_profile_directory / '.aws' / 'sso' / 'cache'
        sso_cache_files = sso_cache_directory.glob('*.json')
        sso_cache_file = max(sso_cache_files, key=lambda x: x.stat().st_mtime)

        self.access_token = json.loads(sso_cache_file.read_text())['accessToken']

        self.client = boto3.client('sso', region_name=self.region)


    def getAccounts(self):
        return self.client.list_accounts(accessToken=self.access_token)
    
    def getCreds(self, account):
        try:
            return self.client.get_role_credentials(
                accountId=account['accountId'], accessToken=self.access_token, roleName='AWSPowerUserAccess')
        except ClientError as e:
            print(account['accountId'], e)
            return

@dataclass
class Credentials:
    access_key: str
    secret_access_key: str
    aws_session_token: str