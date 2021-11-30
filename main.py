# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
from analyzer.dns_layer.functional import ttl
from package_parser import pcap_parser_generator

if __name__ == '__main__':

    pcap = pcap_parser_generator('D:\\Dataset\\botnet\\botnet2014\\ISCX_Botnet-Testing.dns.pcap')

    for eth, ip, udp, dns in pcap:
        a = ttl.ttl_filter(dns)
