# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com


from package_parser import pcap_parser_generator


def domain_name_A_record(pcap_path):
    pcap = pcap_parser_generator(pcap_path)

    for _, ip, _, dns in pcap:
        pass
