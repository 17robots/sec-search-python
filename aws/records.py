
class LogEntry:
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
