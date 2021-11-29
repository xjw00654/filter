# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import os
import time

from utils import download_url_to_file

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
    'cisco_umbrella': 'https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'
}


def download_whitelist(
        time_strap: float
) -> str:
    """ 根据链接下载city、country、asn号所存储的数据库文件
    :param name_data_type: 所要下载的数据库文件类型，asn、county、city，或是以list的形式给出多个
    :param time_strap: 时间戳，文件保存会以时间戳的形式创建保存在文件夹
    :return: 完整文件路径
    """

    # 开始处理
    if time_strap is None:
        raise Exception(
            '参数错误，时间戳不能为空，否则asn数据库，地区数据库以及城市数据库将会下载到三个不同的文件夹下，造成读取错误。')

    dst = os.path.abspath(f'../../../static_files/v2ray-rules/{time_strap}')
    for name, url in V2RAY_RULES_URLs.items():
        # 首先下载哈希值
        os.makedirs(dst, exist_ok=True)  # 创建文件夹保存

        print(f'正在下载{name}实际数据库文件...')
        download_url_to_file(url, f'{dst}/{os.path.basename(url)}', user_agent=_UA)

    dst = os.path.abspath(f'../../../static_files/top1m/{time_strap}')
    for name, url in TOP1m_URLs.items():
        # 首先下载哈希值
        os.makedirs(dst, exist_ok=True)  # 创建文件夹保存

        print(f'正在下载{name}实际数据库文件...')
        download_url_to_file(url, f'{dst}/{name}', user_agent=_UA)

    return dst


def generate_whitelist_domain_names(
        download_new_rules_file: bool = True,
        force: bool = False
) -> str:
    """ 生成域名白名单，包含v2ray-rules以及alexa-1m历史排名数据
    :param download_new_rules_file: 是否要下载新的域名白名单规则数据
    :param force: 是否强制更新，否则一天默认距离上一次下载24小时候才允许更新
    :return: 白名单文件的路径
    """

    whitelite_file_folder = []
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
                fresh_downloaded_time = sorted(os.listdir('../../../static_files/GeoIP2-Lite'))[-1]
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
            _folder = download_whitelist(time_strap=time.time())
        else:
            _folder = os.path.join(dst_path, sorted(os.listdir(dst_path))[-1])
        whitelite_file_folder.append(_folder)

    domain_names = []
    for txt in os.listdir(_folder):
        domain_names += [e.strip() for e in open(os.path.join(_folder, txt)).readlines()]
    domain_names += [e.strip().split(',')[-1] for e in open('../../../static_files/top-1m.csv').readlines()]
    a = 10

    # 加入alexa排名数据
    _alexa_folder = '../../static_files/top-1m.csv'

    return _folder


if __name__ == '__main__':
    print(generate_whitelist_domain_names(False))
