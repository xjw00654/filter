# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import dpkt.dns


def ttl_filter(
        eth: dpkt.ethernet.Ethernet,
        ip: dpkt.ip.IP,
        udp: dpkt.udp.UDP,
        dns: dpkt.dns.DNS,
        ttl_threshold: int = 300
) -> bool:
    """
    dns ttl 过滤器
    :param eth: dpkt.ethernet.Ethernet层对象
    :param ip: dpkt.ip.IP层对象
    :param udp: dpkt.udp.UDP层对象
    :param dns: dkpt.dns.DNS层对象
    :param ttl_threshold: ttl时间过滤阈值，默认为300
    :return: 是否是满足TTL要求的标志
    """
    if dns.an:
        if dns.an.ttl < ttl_threshold:
            return True

    return False
