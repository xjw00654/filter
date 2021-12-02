# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import socket

import dpkt.dns

from package_parser import pcap_parser_generator

RCODE_DICT: dict[int, str] = {
    0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL",
    3: "NXDOMAIN", 4: "NOTIMP", 5: "REFUSED",
    6: "YXDOMAIN", 7: "XRRSET", 8: "NOTAUTH",
    9: "NOTZONE"
}


def _construct_element(_ip, _dns):
    return {
        'id': _dns.id,
        'ip_len': _ip.len,
        'dns_rcode': _dns.rcode,
        'dns_rcode_msg': RCODE_DICT[_dns.rcode],
        'ip_5': (socket.inet_ntoa(_ip.src), _ip.data.sport,
                 socket.inet_ntoa(_ip.dst), _ip.data.dport,
                 _ip.len,),
    }


def pcap_same_src_ip(
        pcap: pcap_parser_generator,
):
    """
    在整个pcap里面找到同一个请求源的所有会话包

    :param pcap: dns_filter.package_parser.pcap_parser_generator对象
    :return:
    """

    ip_pkgs_info = {}
    for i, (ts, (_, ip, _, dns)) in enumerate(pcap):
        if dns.qr == dpkt.dns.DNS_Q:
            _d = ip_pkgs_info.get(socket.inet_ntoa(ip.src), {'Q': [], 'R': [], })
            _d['Q'].append(_construct_element(ip, dns))
            ip_pkgs_info[socket.inet_ntoa(ip.src)] = _d
        elif dns.qr == dpkt.dns.DNS_R:
            _d = ip_pkgs_info.get(socket.inet_ntoa(ip.dst), {'Q': [], 'R': [], })
            _d['R'].append(_construct_element(ip, dns))
            ip_pkgs_info[socket.inet_ntoa(ip.dst)] = _d
        else:
            print('报文类型错误，仅支持查询、响应类型的报文')

    # 后处理一下，统计数据
    for ip_idx, info in ip_pkgs_info.items():
        Q, R = info['Q'], info['R']

    return a


if __name__ == '__main__':
    pcap = pcap_parser_generator('D:\\Dataset\\botnet\\botnet2014\\ISCX_Botnet-Testing.dns.pcap')

    a = pcap_same_src_ip(pcap)
    aa = 10
