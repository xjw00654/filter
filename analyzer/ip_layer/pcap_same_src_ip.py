# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

"""
pcap_same_src_ip.py
处理同ip发出的DNS报文数据，并总结为一个结果字典

主要使用函数pcap_same_src_ip
"""

import socket

import dpkt.dns
import numpy as np
from tqdm import tqdm

from package_parser import pcap_parser_generator

RCODE_DICT: dict[int, str] = {
    0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL",
    3: "NXDOMAIN", 4: "NOTIMP", 5: "REFUSED",
    6: "YXDOMAIN", 7: "XRRSET", 8: "NOTAUTH",
    9: "NOTZONE"
}


def _construct_element(ts, _ip, _dns):
    return {
        'id': _dns.id,
        'timestamp': ts,
        'ip_len': _ip.len,
        'dns_rcode': _dns.rcode,
        'dns_rcode_msg': RCODE_DICT[_dns.rcode],
        'ip_5': (socket.inet_ntoa(_ip.src), _ip.data.sport,
                 socket.inet_ntoa(_ip.dst), _ip.data.dport,
                 _ip.len,),
    }


def pcap_same_src_ip(
        pcap_g: pcap_parser_generator,
) -> dict:
    """
    在整个pcap里面找到同一个请求源的所有会话包

    :param pcap_g: dns_filter.package_parser.pcap_parser_generator对象
    :return: 结果字典，包含Q,R,pair,unpair前面两个表示请求和响应数据，后面两个表示匹配的请求数据和不匹配的响应数据，
                     - Q,R的内部元素都是列表，列表中的元素为字典，代表一个请求的简略数据，
                            包含会话id，时间戳，dns的错误码，dns的错误码的详细信息，ip五元组数据。
                     - pair和unpar的内部元素都是字典，字典的K为会话ID，同ID的报文会归到一个list里，
                                                  字典的V也是字典，包含Q和R两个字段，这两个字典的值同上。
    """

    ip_pkgs_info = {}
    for ts, (_, ip, _, dns) in pcap_g:
        if dns.qr == dpkt.dns.DNS_Q:
            _d = ip_pkgs_info.get(socket.inet_ntoa(ip.src), {'Q': [], 'R': [], })
            _d['Q'].append(_construct_element(ts, ip, dns))
            ip_pkgs_info[socket.inet_ntoa(ip.src)] = _d
        elif dns.qr == dpkt.dns.DNS_R:
            _d = ip_pkgs_info.get(socket.inet_ntoa(ip.dst), {'Q': [], 'R': [], })
            _d['R'].append(_construct_element(ts, ip, dns))
            ip_pkgs_info[socket.inet_ntoa(ip.dst)] = _d
        else:
            print('报文类型错误，仅支持查询、响应类型的报文')

    # 后处理一下，统计数据
    _pair_unpair_data = {}
    for ip_idx, info in tqdm(ip_pkgs_info.items()):
        Q, R = np.array(info['Q']), np.array(info['R'])

        q_id_index = np.array([e['id'] for e in Q])
        r_id_index = np.array([e['id'] for e in R])

        pair_id_index = set(q_id_index) & set(r_id_index)
        unpair_query_id_index = (set(q_id_index) | set(r_id_index)) - set(r_id_index)
        unpair_resposne_id_index = (set(q_id_index) | set(r_id_index)) - set(q_id_index)

        pair, unpair = {}, {}
        for _id in pair_id_index:
            pair[_id] = {
                'Q': Q[q_id_index == _id],
                'R': R[r_id_index == _id],
            }
        for _id in unpair_query_id_index:
            unpair[_id] = {'Q': Q[q_id_index == _id], }
        for _id in unpair_resposne_id_index:
            unpair[_id] = {'R': R[r_id_index == _id], }

        ip_pkgs_info[ip_idx]['pair'] = pair
        ip_pkgs_info[ip_idx]['unpair'] = unpair

    return ip_pkgs_info


if __name__ == '__main__':
    pcap = pcap_parser_generator('D:\\Dataset\\botnet\\botnet2014\\ISCX_Botnet-Testing.dns.pcap')

    a = pcap_same_src_ip(pcap)
