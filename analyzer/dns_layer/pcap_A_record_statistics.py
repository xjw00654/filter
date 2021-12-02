# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import socket
from collections import defaultdict
from functools import partial

import dpkt.dns

from package_parser import pcap_parser_generator


def pcap_A_record_statistics(
        pcap: pcap_parser_generator,
        *,  # 后面得给爷写完整咯，到底要asn，country还是city
        do_asn_query: bool = False,
        do_city_query: bool = False,
        do_country_query: bool = False
) -> dict:
    """
    在整个pcap里面找到单个域名的A记录个数，同时支持ASN记录查询

    :param pcap: dns_filter.package_parser.pcap_parser_generator对象
    :param do_asn_query: 是否要进行ASN查询
    :param do_city_query: 是否要进行City查询
    :param do_country_query: 是否要进行Country查询
    :return: 返回域名A记录数据，字典K为域名(str)，V为字典，其中K为IP，V为TTL集合或是字典，
    """

    i = 0
    domain_ip_map = defaultdict(set)
    for i, (ts, (_, ip, _, dns)) in enumerate(pcap):
        if dns.qr != dpkt.dns.DNS_R:  # 请求不要，只拿响应数据
            continue
        if len(dns.an) < 1:  # 回答数据不足的，也直接不管了
            continue

        for answer in dns.an:
            if answer.type == dpkt.dns.DNS_A:  # DNS_A记录
                domain_ip_map[answer.name].add((socket.inet_ntoa(answer.ip), answer.ttl))
    print(f'一共{i}条DNS数据，共筛选出{len(domain_ip_map.keys())}条响应记录')

    domain_ip_map = dict(domain_ip_map)
    print(f'正在处理响应数据，统计IP计数，同时统计TTL...')
    for domain_name, ip_ttl_list in domain_ip_map.items():
        _stat = defaultdict(partial(defaultdict, set))  # 要整一个偏函数才能保证嵌套df
        for elem in ip_ttl_list:
            _stat[elem[0]]['ttl'].add(elem[1])

        domain_ip_map[domain_name] = dict(_stat)
    print('完成，返回字典数据，字典K为域名(str)，V为字典，其中K为IP，V为TTL集合')

    if do_asn_query or do_country_query or do_city_query:
        print(f'正在初始化geoip2-lite查询客户端...')
        from analyzer.dns_layer.functional.ip_geoIP import Client
        client = Client(False)

        print(f'初始化完成，正在进行数据查询...')
        for domain_name, IPs in domain_ip_map.items():
            IPs_add_asn = dict()
            for ip, ttl in IPs.items():
                IPs_add_asn[ip] = {
                    'ttl': list(ttl),
                    'asn': [elem for elem in
                            [e['asn'] for e in client.query_asn(ip)] if isinstance(elem, int)] if do_asn_query else [],
                    'country': client.query_country(ip) if do_country_query else [],
                    'city': client.query_city(ip) if do_city_query else [],
                }
            domain_ip_map[domain_name] = IPs_add_asn

        print('完成，返回字典数据，字典K为域名(str)，V为字典，其中K为IP，V为字典，K为IP，V为ttl,asn,city,country等查询值')

    return domain_ip_map


if __name__ == '__main__':
    pcap = pcap_parser_generator('D:\\Dataset\\botnet\\botnet2014\\ISCX_Botnet-Testing.dns.pcap')

    a = pcap_A_record_statistics(pcap, do_asn_query=True, do_city_query=True, do_country_query=True)
    aa = 10
