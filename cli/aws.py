from aws.sec_groups import grab_sec_groups
from aws.instances import grab_instances
from cli.cli import CLI
from .common import command_arguments
from aws.aws_search import AWS
from aws.sso import SSO
import boto3


@command_arguments
def aws(sources, regions, dests, display, accounts, ports, protocols, output, query):
    cli = CLI(subcommand="demo", sources=sources, regions=regions, dests=dests,
              protocols=protocols, accounts=accounts, ports=ports, output=output, cloudquery=query)
    searcher = AWS()
    searcher.search(cli)


    # print('After Filtering')
    # for region in searcher.ruleMap:
    #     for account in searcher.ruleMap[region]:
    #         if(len(searcher.ruleMap[region][account])) > 0:
    #             print("{} account {}: {} instances".format(
    #                 region, account, len(searcher.ruleMap[region][account])))
