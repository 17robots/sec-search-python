import boto3.session
import click
import boto3
import json
import os
from botocore.exceptions import ClientError
from pathlib import Path
from aws.sso import SSO
from aws.sec_groups import grab_sec_groups

@click.command()
def aws():
    grab_sec_groups()
