# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import logging
import multiprocessing as mp
import os
import pickle
import shutil
import time
from collections import Counter
from functools import reduce

import dpkt

from package_parser import pcap_parser_generator

logger = logging.Logger('FastFlucos')


def _process(pcap_path):
    pcap = pcap_parser_generator(pcap_path)
    domain_names = [[e.name for e in packet[1][-1].an] for packet in pcap]
    return domain_names


def get_full_domain_name(pcap_folder):
    pcap_list = [os.path.join(pcap_folder, e) for e in os.listdir(pcap_folder) if e.endswith('.pcap')]

    # 验证pcap包有效性
    valid_pcap_list = []
    for e in pcap_list:
        try:
            dpkt.pcap.Reader(open(e, 'rb'))
        except ValueError:
            logger.warning(f"{e}包存在问题，无法读取，将会跳过。")
        else:
            valid_pcap_list.append(e)
    logger.info(f'共找到有效数据包{len(valid_pcap_list)}个。')

    pool = mp.Pool(processes=mp.cpu_count())
    results = pool.map(_process, valid_pcap_list)
    pool.close()
    pool.join()

    results = reduce(lambda x, y: x + y, results)
    domain_names_counter = Counter([dn for res in results for dn in res])

    return domain_names_counter, results


def match_first_second(first_dn, second_dn_list):
    # _first_second_rule1
    pass


if __name__ == '__main__':
    pcap_folder = 'c:\\Users\\FH\\Desktop\\dns_pcap\\1229'
    # 预处理：步骤零：将完整的一天的数据分成五分钟一个的文件夹，总计288个
    file_list = [e for e in os.listdir(pcap_folder) if e.endswith('.pcap')]
    if file_list:
        file_name2time = {time.mktime(time.strptime(e, '%Y_%m%d_%H%M_%Swl.pcap')): e for e in file_list}

        file_time_sorted = sorted(list(file_name2time.keys()))
        start_time = file_time_sorted[0]
        num_subsets = (file_time_sorted[-1] - file_time_sorted[0] + 60) // (5 * 60)

        logger.info(f'正在进行时间分片，最后不足5min的分片数据将会被丢弃')
        time_subset, file_subset = [], []
        for i in range(int(num_subsets)):
            sub = [start_time + sec for sec in range(0, 300, 60)]

            start_time += 300
            time_subset.append(sub)
            name_sub = [file_name2time.get(e, None) for e in sub]

            target_folder = os.path.join(pcap_folder, str(i))
            os.makedirs(target_folder, exist_ok=True)
            for idx, name in enumerate(name_sub):
                try:
                    shutil.move(os.path.join(pcap_folder, name), os.path.join(target_folder, name))
                except FileExistsError:
                    continue
            file_subset.append(name_sub)
    else:
        logger.info('似乎已经完成了数据分片')

    # 预处理：步骤一，找到完整的First域名
    subset_list = os.listdir(pcap_folder)
    subset_domain_names = [get_full_domain_name(os.path.join(pcap_folder, e)) for e in subset_list]

    pickle.dump(subset_domain_names, open('data.pkl', 'wb'))

    # first_domain_names = list(set(reduce(lambda x, y: x + y, [list(e[0].keys()) for e in subset_domain_names])))
    # logger.info(f'一共获取到{len(first_domain_names)}条不重复域名')
    #
    # # 预处理：步骤二：找到First域名对应的Second域名数
    # a = 10
