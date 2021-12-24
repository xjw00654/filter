# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import multiprocessing as mp
import os
import shutil
import socket
import time

import dpkt
import pydblite

from package_parser import pcap_parser_generator


def get_cdn_ip():
    import struct
    cdn_ip = [e.strip().split(',')[-1]
              for e in open('cdn_ip_202112231856.csv', 'r', encoding='utf-8').readlines()][1:]
    s = time.time()
    print('开始创建CDN IP内存数据库')
    pydb = pydblite.Base(':memory:')
    pydb.create('cdnIP')
    pydb.create_index('cdnIP')
    for elem in cdn_ip:
        pydb.insert(cdnIP=socket.inet_ntoa(struct.pack('I', socket.htonl(int(elem)))))
    print(f'cdnIP数据库创建完成，耗时{time.time() - s}')
    return pydb


def get_wl_db():
    ts = sorted(os.listdir('top1m'))
    _p = os.path.join('top1m', ts[-1])
    full_data = []
    for tp in os.listdir(_p):
        _p_csv = os.path.join(_p, tp, 'top-1m.csv')
        full_data += [e.strip().split(',')[1] for e in open(_p_csv, 'r').readlines()]

    wl = []
    for dn in full_data:
        spl = dn.split('.')
        if len(spl) < 2:
            continue
        if spl[-2] == 'com':
            if len(spl) == 2:
                continue
            else:
                wl.append(spl[-3])
        else:
            wl.append(spl[-2])
    wl = sorted(list(set(wl)))
    s = time.time()
    print('开始创建白名单内存数据库')
    pydb = pydblite.Base(':memory:')
    pydb.create('domain_name')
    pydb.create_index('domain_name')
    for elem in wl:
        pydb.insert(domain_name=elem)
    print(f'白名单数据库创建完成，耗时{time.time() - s}')
    return pydb


def sent_data(
        path: str,
        q: mp.Queue,
        num_processes=8,
):
    """
    在path目录里监测文件变化，并将数据送入到q队列里面

    :param path: 需要监测的文件夹
    :param q: 数据队列
    :param num_processes: 用来终止进程
    :return: None
    """

    def time2strap(tm):
        return str(int(time.mktime(time.strptime(tm, '%Y_%m%d_%H%M_%S'))))

    processed = []
    do_continue_times = 0
    while True:
        files = [e for e in os.listdir(path) if 'wl' not in e]  # 带wl的是有处理完成的
        if len(set(files) - set(processed)) < num_processes + 1:
            time.sleep(10)
            do_continue_times += 1
            if do_continue_times >= 360:  # 超过3600秒没有新数据产生，直接break掉
                break
            continue
        else:
            do_continue_times = 0
            ll = list(set(files) - set(processed))
            lld = {
                e: time2strap(e.replace('.pcap', '')) for e in ll
            }
            lld_r = {
                v: k for k, v in lld.items()
            }
            ll_time_strap_sorted = sorted(list(lld.values()))[:-1]  # 最新的一个暂时不弄

            for _f in ll_time_strap_sorted:
                _f = os.path.join(path, lld_r[_f])  # 把完成路径给出来
                try:
                    if _f not in processed:
                        processed.append(_f)
                        q.put_nowait(_f)
                    else:
                        continue
                except Exception:
                    print(_f, '在传输数据到队列时遇到错误，请人工处理')

    for _f in list(set(files) - set(processed)):  # 剩下一些东西，也要跑一下
        _f = os.path.join(path, _f)  # 把完成路径给出来
        try:
            if _f not in processed:
                processed.append(_f)
                q.put_nowait(_f)
            else:
                continue
        except Exception:
            print(_f, '在传输数据到队列时遇到错误，请人工处理')
    for i in range(num_processes):
        q.put_nowait('STOP')


def filter_wl(
        q: mp.Queue,
        pydb_wl: pydblite.Base,
        pydb_ip: pydblite.Base
):
    """
    从队列q里面取数据，取数据做处理并保存

    :param q: 数据队列
    :param pydb_wl: 白名单数据库对象
    :param pydb_ip: cdn ip白名单对象
    :return: None
    """
    while True:
        try:
            _f = q.get_nowait()
            if _f is None:
                time.sleep(1)
                continue
        except Exception as e:
            time.sleep(1)
            continue
        if _f == 'STOP':
            print('GET STOP !!')
            break

        print('GET: ', _f)
        pcap = pcap_parser_generator(_f)
        fw = open(_f.replace('.pcap', 'wl.pcap'), 'wb')
        writer = dpkt.pcap.Writer(fw)

        num_writes = 0
        for ts, (eth, _, _, dns) in pcap:
            if dns.qr != dpkt.dns.DNS_R:  # 请求不要，只拿响应数据
                continue
            if len(dns.an) < 1:  # 回答数据不足的，也直接不管了
                continue

            in_wl_nums = 0
            for qd in dns.qd:
                dn = qd.name
                dn_spl = dn.split('.')
                dn_sld = ""
                if len(dn_spl) < 2:
                    continue
                if dn_spl[-2] == 'com':
                    if len(dn_spl) == 2:
                        continue
                    dn_sld = dn_spl[-3]
                else:
                    dn_sld = dn_spl[-2]
                if pydb_wl(domain_name=dn_sld):
                    in_wl_nums += 1

            ttl_ok_nums = 0  # 似乎不顶啥用
            for an in dns.an:
                if an.ttl > 1800:
                    ttl_ok_nums += 1

            cdn_ip_ok_nums = 0
            for an in dns.an:
                if hasattr(an, 'ip'):
                    real_ip = socket.inet_ntoa(an.ip)
                    if pydb_ip(cdnIP=real_ip):
                        cdn_ip_ok_nums += 1

            # 有不在白名单的an；有不在白名单的ip；有小于1800的ttl记录（不管A还是CNAME还是其他）
            if len(dns.qd) != in_wl_nums and \
                    len(dns.an) != ttl_ok_nums and \
                    len(dns.an) != cdn_ip_ok_nums:
                writer.writepkt(eth, ts=ts)
                num_writes += 1

        print(f'{_f}一共剩下{num_writes}个数据包')

        shutil.move(_f, _f.replace('.pcap', 'wl.pcap'))
        # os.remove(_f)


if __name__ == '__main__':
    pcap_path = 'c:\\Users\\JiaweiXie\\Desktop\\dns_pcap'
    pydb_ip = get_cdn_ip()
    pydb_wl = get_wl_db()
    q = mp.Queue()

    n = 8
    p_set = []
    for i in range(n):
        p = mp.Process(target=filter_wl, args=(q, pydb_wl, pydb_ip))
        p.start()
        p_set.append(p)
    s_p = mp.Process(target=sent_data, args=(pcap_path, q, n))
    s_p.start()
    for p in p_set:
        p.join()

    print('DONE')
