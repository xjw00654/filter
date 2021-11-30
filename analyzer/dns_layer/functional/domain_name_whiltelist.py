# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import os
import time

from utils import download_url_to_file, unzip

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
      'AppleWebKit/537.36 (KHTML, like Gecko) ' \
      'Chrome/96.0.4664.55 ' \
      'Safari/537.36 ' \
      'Edg/96.0.1054.34'

V2RAY_RULES_URLs = {
    # 直连域名
    'direct': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/direct-list.txt",
    # 代理域名
    'proxy': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/proxy-list.txt",
    # 广告域名
    'ad': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/reject-list.txt",
    # GFW
    'gfw': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/gfw.txt",
    # greatfire
    'greatfire': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/greatfire.txt",
    # windows隐私跟踪域名
    'winspy': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/win-spy.txt",
    # windows系统更新域名
    'winup': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/win-update.txt",
    # windows附加隐私跟踪域名
    'winextra': "https://cdn.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/win-extra.txt",
}
TOP1m_URLs = {
    # https://hackertarget.com/top-million-site-list-download/
    'cisco_umbrella': 'https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip',
    'alexa': 'https://s3.amazonaws.com/alexa-static/top-1m.csv.zip',
    'tranco': 'https://tranco-list.eu/top-1m.csv.zip',
}


def download_whitelist(
        time_strap: float,
        top1m: bool,
        v2ray: bool,
) -> list:
    """
    根据链接下载city、country、asn号所存储的数据库文件

    :param name_data_type: 所要下载的数据库文件类型，asn、county、city，或是以list的形式给出多个
    :param time_strap: 时间戳，文件保存会以时间戳的形式创建保存在文件夹
    :param v2ray: 是否要下载v2ray数据
    :param top1m: 是否要下载top1m数据
    :return: 完整的文件路径
    """

    # 开始处理
    if time_strap is None:
        raise Exception(
            '参数错误，时间戳不能为空，否则asn数据库，地区数据库以及城市数据库将会下载到三个不同的文件夹下，造成读取错误。')

    dst_return = []
    if v2ray:
        dst = os.path.abspath(f'../../../static_files/v2ray-rules/{time_strap}')
        for name, url in V2RAY_RULES_URLs.items():
            # 首先下载哈希值
            os.makedirs(dst, exist_ok=True)  # 创建文件夹保存

            print(f'正在下载{name}实际数据库文件...')
            download_url_to_file(url, f'{dst}/{os.path.basename(url)}', user_agent=_UA)
        dst_return.append(dst)

    if top1m:
        dst = os.path.abspath(f'../../../static_files/top1m/{time_strap}')
        for name, url in TOP1m_URLs.items():
            # 首先下载哈希值
            os.makedirs(dst, exist_ok=True)  # 创建文件夹保存

            print(f'正在下载{name}实际数据库文件...')
            download_url_to_file(url, f'{dst}/{os.path.basename(url)}', user_agent=_UA)

            # 解压缩
            print(f'正在解压{name}实际数据库文件...')
            try:
                unzip(f'{dst}/{os.path.basename(url)}', os.path.join(dst, name))
            except Exception as e:
                raise Exception(f"解压错误，解压过程发生错误，请检查{e}")
            else:
                print('正在删除压缩文件...')
                os.remove(f'{dst}/{os.path.basename(url)}')  # 未发生错误，删除压缩文件
        dst_return.append(dst)

    if top1m ^ v2ray:
        return dst_return
    else:
        return [os.path.abspath(f'../../../static_files/v2ray-rules/{time_strap}'),
                os.path.abspath(f'../../../static_files/top1m/{time_strap}')]


def generate_whitelist_domain_names(
        download_new_rules_file: bool = True,
        force: bool = False
) -> dict:
    """
    生成域名白名单，包含v2ray-rules以及alexa-1m历史排名数据

    :param download_new_rules_file: 是否要下载新的域名白名单规则数据
    :param force: 是否强制更新，否则一天默认距离上一次下载24小时候才允许更新
    :return: 字典，字典三个KV为TLD,TLD_except以及DN，分别代表顶级域名列表（去重）、去除顶级域名后的域名（去重）以及完整域名列表
    """
    _folders = []
    for dst_path in ['../../../static_files/v2ray-rules', '../../../static_files/top1m']:
        if not download_new_rules_file and (not os.path.exists(dst_path) or len(os.listdir(dst_path)) == 0):
            # 不要下载，但是却没有找到数据库文件
            print('当前没有找到任何下载完成的数据库文件，将会自动进行下载，请确保网络通常')
            download_new_rules_file = True
        elif not download_new_rules_file and (not os.path.exists(dst_path) or len(os.listdir(dst_path)) != 0):
            # 不要下载，且已找到了
            download_new_rules_file = False
        elif download_new_rules_file:  # 要下载
            if os.path.exists(dst_path) and len(os.listdir(dst_path)) != 0:
                # 已经有一些一下载的东西了，检查一下日期，小于一天，且根据force字段的值判断是否真的要下载
                fresh_downloaded_time = sorted(os.listdir(dst_path))[-1]
                if time.time() - float(fresh_downloaded_time) < 86400:
                    if not force:
                        print('距离上一次更新数据库时间小于1天，请尽可能减小更新频率，如果需要强制更新，请使用force=True')
                        download_new_rules_file = False
                    else:
                        print('距离上一次更新数据库时间小于1天，将会进行强制数据库更新')
                        download_new_rules_file = True  # 显示写出来，便于理解
                else:
                    download_new_rules_file = True  # 显示写出来，便于理解
        else:
            raise Exception('逻辑错误，好像你遇到了一些我没有考虑到的事情.... by:jwxie :D')

        if download_new_rules_file:
            _folders += download_whitelist(time_strap=time.time(), top1m='top1m' in dst_path, v2ray='v2ray' in dst_path)
        else:
            _folders += [os.path.join(dst_path, sorted(os.listdir(dst_path))[-1])]

    domain_names = []
    for _folder in _folders:
        # 按顺序处理top1m和v2ray
        for txt in os.listdir(_folder):
            if 'v2ray' in _folder:
                domain_names += [e.strip() for e in open(os.path.join(_folder, txt)).readlines()]
            elif 'top1m' in _folder:
                domain_names += [e.strip().split(',')[-1] for e in
                                 open(os.path.join(_folder, txt, 'top-1m.csv')).readlines()]
            else:
                raise Exception('支持错误，还没有实现对该类数据的支持')

    return {
        'DN': list(set(domain_names)),
        'TLD': list(set([e.split('.')[-1] for e in domain_names if '.' in e])),
        'TLD_except': list(set([e.split('.')[:-1] for e in domain_names if '.' in e]))
    }

    if __name__ == '__main__':
        print(generate_whitelist_domain_names(False))
