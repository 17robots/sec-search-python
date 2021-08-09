from pprint import pprint
from datetime import datetime, timedelta
import boto3
import functools
import logging
import time

#logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

log_group_name = 'tf-vpc-flow-logs'
message_pattern = '/(?<version>\S+)\s+(?<account_id>\S+)\s+(?<interface_id>\S+)\s+(?<srcaddr>\S+)\s+(?<dstaddr>\S+)\s+(?<srcport>\S+)\s+(?<dstport>\S+)\s+(?<protocol>\S+)\s+(?<packets>\S+)\s+(?<bytes>\S+)\s+(?<start>\S+)\s+(?<end>\S+)\s+(?<action>\S+)\s+(?<log_status>\S+)(?:\s+(?<vpc_id>\S+)\s+(?<subnet_id>\S+)\s+(?<instance_id>\S+)\s+(?<tcp_flags>\S+)\s+(?<type>\S+)\s+(?<pkt_srcaddr>\S+)\s+(?<pkt_dstaddr>\S+))?(?:\s+(?<region>\S+)\s+(?<az_id>\S+)\s+(?<sublocation_type>\S+)\s+(?<sublocation_id>\S+))?(?:\s+(?<pkt_src_aws_service>\S+)\s+(?<pkt_dst_aws_service>\S+)\s+(?<flow_direction>\S+)\s+(?<traffic_path>\S+))?/'


def query(filter_string):
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)
    query_id = client.start_query(logGroupName=log_group_name, startTime=int(start_time.timestamp()), endTime=int(
        end_time.timestamp()), queryString=f'parse @message {message_pattern} | filter {filter_string}')['queryId']
    results = []
    while True:
        response = client.get_query_results(queryId=query_id)
        logger.info(' '.join([response['status'], str(
            len(response['results'])), 'results']))
        results.extend(response['results'])
        if response['status'] == 'Complete':
            break
    logger.info(' '.join([str(len(results)), 'results']))
    pprint(results)
    return results


def watch(partial, seconds):
    while True:
        partial()
        time.sleep(seconds)


if __name__ == '__main__':
    client = boto3.client('logs', region_name='eu-west-2')

#watch(functools.partial(query, 'pkt_srcaddr="10.198.37.196" and dstport="1433"'), 60)

results = query('pkt_srcaddr="10.198.37.196" and dstport="1433"')
pprint(results)

"""
timestamp = int(
                                (datetime.now() - timedelta(minutes=1)).timestamp())
                            endstamp = int(
                                (datetime.now() + timedelta(minutes=5)).timestamp())
                            try:
                                paginator = client.get_paginator('filter_log_events').paginate(
                                    logGroupName=name,
                                    startTime=timestamp * 1000,
                                    endTime=endstamp * 1000,
                                    filterPattern="?ACCEPT ?REJECT",
                                    PaginationConfig={
                                        'PageSize': 1
                                    }
                                ).search(SearchFilters.events.value)
                                val = next(paginator, None)
                                while val is not None:
                                    if killEvent.is_set():
                                        return
                                    entry = LogEntry(
                                        val['timestamp'], val['message'])
                                    if cli.allowEntry(entry=entry):
                                        msgPmp.put(
                                            common.event.LogEntryReceivedEvent(
                                                log="[{}]{} {} {} {} {} {} {}[/{}]".format("green" if entry.action == "ACCEPT" else "red", entry.timestamp, entry.pkt_srcaddr, entry.pkt_dstaddr, entry.srcport, entry.dstport, entry.action, entry.flow_direction, "green" if entry.action == "ACCEPT" else "red"))
                                        )
                                    else:
                                        common.event.LogEntryReceivedEvent(
                                            log="Log Failed Filter"
                                        )
                                    val = next(paginator, None)
                                    sleep(.5)
                            except Exception as e:
                                common.event.ErrorEvent(
                                    e=e
                                )
                                break

                        msgPmp.put(
                            common.event.LogStreamStopped(region=region))
                        return









                        with clientLock:
                                    threadClient = boto3.client('logs', region_name=region, aws_access_key_id=creds.access_key,
                                            aws_secret_access_key=creds.secret_access_key, aws_session_token=creds.session_token)
                                fullQuery = f"fields @timestamp, @message | parse @message {message_pattern} {cli.buildFilters()}"
                                with open('log.txt', 'a') as f:
                                    f.write(f"queryString: {fullQuery}\n")
                                end_time = datetime.now()
                                start_time = end_time - timedelta(minutes=5)
                                query_id = threadClient.start_query(logGroupName=name, startTime=int(start_time.timestamp()), endTime=int(
                                    end_time.timestamp()), queryString=fullQuery)['queryId']
                                results = []
                                while True:
                                    response = threadClient.get_query_results(
                                        queryId=query_id)
                                    results.extend(response['results'])
                                    if response['status'] == 'Complete':
                                        break
                                for result in results:
                                    common.event.LogEntryReceivedEvent(
                                        log=' '.join([val['value']
                                                      for val in result])
                                    )
                                time.sleep(.5)
                            except Exception as e:
                                common.event.ErrorEvent(e=e)
                                with open('log.txt', 'a') as f:
                                    f.write(
                                        f"We Encountered An Error: {str(e)}\n")
                                break
                        msgPmp.put(
                            common.event.LogStreamStopped(region=region))
                        return
"""
