import click
from aws.sec_groups import grab_sec_groups
from aws.sec_group_rules import grab_sec_group_rules
from aws.instances import grab_instances


@click.command()
def aws():
    # grab_sec_group_rules()
    # grab_sec_groups()
    grab_instances()
