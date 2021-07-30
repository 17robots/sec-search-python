
class LogEntry:
    # __slots__ = [
    #     'timestamp',
    #     'version',
    #     'account_id',
    #     'interface_id',
    #     'srcaddr'
    #     'dstaddr',
    #     'srcport',
    #     'dstport',
    #     'protocol',
    #     'packets',
    #     'bytes',
    #     'start',
    #     'end',
    #     'action',
    #     'log_status',
    #     'vpc_id',
    #     'subnet_id',
    #     'instance_id',
    #     'tcp_flags',
    #     'type',
    #     'pkt_srcaddr',
    #     'pkt_dstaddr',
    #     'region',
    #     'az_id',
    #     'sublocation_type',
    #     'sublocation_id',
    #     'pkt_src_aws_service',
    #     'pkt_dst_aws_service',
    #     'flow_direction',
    #     'traffic_path'
    # ]

    def __init__(self, timestamp: str, message: str):
        self.timestamp = timestamp
        messageFields = message.split(' ')
        self.version = messageFields[0]
        self.account_id = messageFields[1]
        self.interface_id = messageFields[2]
        self.srcaddr = messageFields[3]
        self.dstaddr = messageFields[4]
        self.srcport = int(messageFields[5])
        self.dstport = int(messageFields[6])
        self.protocol = messageFields[7]
        self.packets = messageFields[8]
        self.bytes = messageFields[9]
        self.start = messageFields[10]
        self.end = messageFields[11]
        self.action = messageFields[12]
        self.log_status = messageFields[13]
        self.vpc_id = messageFields[14]
        self.subnet_id = messageFields[15]
        self.instance_id = messageFields[16]
        self.tcp_flags = messageFields[17]
        self.type = messageFields[18]
        self.pkt_srcaddr = messageFields[19]
        self.pkt_dstaddr = messageFields[20]
        self.region = messageFields[21]
        self.az_id = messageFields[22]
        self.sublocation_type = messageFields[23]
        self.sublocation_id = messageFields[24]
        self.pkt_src_aws_service = messageFields[25]
        self.pkt_dst_aws_service = messageFields[26]
        self.flow_direction = messageFields[27]
        self.traffic_path = messageFields[28]


""" backup stuff
paginator = client.get_paginator('filter_log_events').paginate(
                                    logGroupName=name,
                                    startTime=timestamp * 1000,
                                    endTime=endstamp * 1000,
                                    filterPattern="?ACCEPT ?REJECT",
                                    PaginationConfig={
                                        'PageSize': 1
                                    },
                                ).search(SearchFilters.events.value)
                                val = next(paginator, None)
                                while val is not None:
                                    if cli.allowEntry(LogEntry(val['timestamp'], val['message'])):
                                        msgPmp.put(
                                            common.event.LogEntryReceivedEvent(
                                                log=str(val))
                                        )
                                    else:
                                        common.event.LogEntryReceivedEvent(
                                            log="Log Failed Filter"
                                        )
                                    val = next(paginator, None)
                                    sleep(.5)
"""
