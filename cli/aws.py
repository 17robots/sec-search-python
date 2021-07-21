from re import L
import click
from aws.sec_groups import grab_sec_groups
from aws.sec_group_rules import grab_sec_group_rules
from aws.instances import grab_instances


@click.command()
def aws():
    instances = grab_sec_group_rules()
    # instances = grab_sec_groups()
    # instances = grab_instances()
    for region in instances:
        for account in instances[region]:
            print("{}, account {}, {} instances".format(region, account,
                                                        len(instances[region][account])))
