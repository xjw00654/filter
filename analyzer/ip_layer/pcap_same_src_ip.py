# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import socket
from collections import defaultdict

import dpkt.dns

from package_parser import pcap_parser_generator

RCODE_DICT = {
    0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL",
    3: "NXDOMAIN", 4: "NOTIMP", 5: "REFUSED",
    6: "YXDOMAIN", 7: "XRRSET", 8: "NOTAUTH",
    9: "NOTZONE"
}


def pcap_same_src_ip(
        pcap: pcap_parser_generator,
):
    """
    在整个pcap里面找到同一个请求源的所有会话包

    :param pcap: dns_filter.package_parser.pcap_parser_generator对象
    :return:
    """

    _d = defaultdict(list)
    for i, (_, ip, _, dns) in enumerate(pcap):
        src_ip = socket.inet_ntoa(ip.src)
        src_port = ip.data.get('sport')
        dst_ip = socket.inet_ntoa(ip.dst)
        dst_port = ip.data.get('dport')

        if dns.qr == dpkt.dns.DNS_Q:
            _d[id].append({
                'is_query': True,
                'is_response': False
            })
        else:
            print('报文类型错误，仅支持查询、响应类型的报文')

        for answer in dns.an:
            a = 10


if __name__ == '__main__':
    pcap = pcap_parser_generator('D:\\Dataset\\botnet\\botnet2014\\ISCX_Botnet-Testing.dns.pcap')

    a = pcap_same_src_ip(pcap)
    aa = 10
