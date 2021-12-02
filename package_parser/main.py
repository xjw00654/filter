# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
from typing import Generator

import dpkt
from tqdm import tqdm


def pcap_parser_generator(
        pcap_path: str
) -> Generator:
    """
    pcap 包解析生成器

    :param pcap_path: pcap包文件所在目录
    :return:  DNS层数据生成器对象，格式为：时间戳，(eth层对象, ip层对象, udp层对象, dns层对象)
    """
    f = open(pcap_path, 'rb')
    pcap_reader = dpkt.pcap.Reader(f)

    n = 0
    for n, (time_strap, data) in enumerate(tqdm(pcap_reader)):
        try:
            eth = dpkt.ethernet.Ethernet(data)
            ip = eth.data
        except:
            continue

        if not isinstance(ip, dpkt.ip.IP) or \
                isinstance(ip, dpkt.ip6.IP6) or \
                ip.p != 17:  # 只保留UDP数据，ip层protocol协议号来进行鉴别
            continue
        else:
            try:
                udp = ip.data
                dns = dpkt.dns.DNS(udp.data)

                if dns.qr != dpkt.dns.DNS_R and dns.qr != dpkt.dns.DNS_Q:  # 同时拿Q和R
                    continue
                if dns.opcode != dpkt.dns.DNS_QUERY:  # 判断是否DNS_QUERY
                    continue
                if dns.rcode != dpkt.dns.DNS_RCODE_NOERR:  # 判断是否是DNS_RCODE_NOERR
                    continue

            except:
                continue  # 不是DNS类型或者出错
            else:
                yield time_strap, (eth, ip, udp, dns)
    print(f'该{pcap_path}文件，共包含{n}条数据')


def pcap_parser(
        pcap_path: str
) -> list:
    """
    pcap 包解析生成器

    :param pcap_path: pcap包文件所在目录
    :return: 列表，包含pcap包内所有DNS层数据，格式为：[时间戳，(eth层对象, ip层对象, udp层对象, dns层对象), ...]
    """
    f = open(pcap_path, 'rb')
    pcap_reader = dpkt.pcap.Reader(f)

    packs = []
    for n, (time_strap, data) in enumerate(tqdm(pcap_reader)):
        try:
            eth = dpkt.ethernet.Ethernet(data)
            ip = eth.data
        except:
            continue

        if not isinstance(ip, dpkt.ip.IP) or \
                isinstance(ip, dpkt.ip6.IP6) or \
                ip.p != 17:  # 只保留UDP数据，ip层protocol协议号来进行鉴别
            continue
        else:
            try:
                udp = ip.data
                dns = dpkt.dns.DNS(udp.data)
            except:
                continue  # 不是DNS类型或者出错
            else:
                packs.append((time_strap, (eth, ip, udp, dns)))
    return packs
