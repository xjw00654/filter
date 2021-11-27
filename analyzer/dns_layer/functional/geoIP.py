````  # coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import os
import time
from typing import List, Union, Tuple

from utils import download_url_to_file

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
      'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
_BASE_URL = f'https://download.maxmind.com/app/geoip_download'
_LICENSE_KEY = 'YzIkjIjASarh4lpT'  # !!jwxie!!

URLs = dict(
    asn=f'{_BASE_URL}?edition_id=GeoLite2-ASN&license_key={_LICENSE_KEY}&suffix=tar.gz',
    city=f'{_BASE_URL}?edition_id=GeoLite2-City&license_key={_LICENSE_KEY}&suffix=tar.gz',
    country=f'{_BASE_URL}?edition_id=GeoLite2-Country&license_key={_LICENSE_KEY}&suffix=tar.gz'
)
SHA256 = {k: v + '.sha256' for k, v in URLs.items()}


def download_mmdb(mmdb_data_type: Union[str, List, Tuple], time_strap: float = None) -> None:
    # 一些简单的参数检查
    if isinstance(mmdb_data_type, str):
        mmdb_data_type = [mmdb_data_type]
    elif isinstance(mmdb_data_type, Tuple) or isinstance(mmdb_data_type, List):
        pass
    else:
        raise Exception('参数错误，mmdb_data_type参数需要一个list或者一个tuple，且内部元素少于三个')

    for e in mmdb_data_type:
        if e not in URLs.keys():
            raise Exception(f'参数错误，当前仅支持{URLs.keys()}的mmdb数据查询，其他类型的数据需要付费。')

    # 开始处理
    dst = os.path.abspath(f'../../../static_files/GeoIP2-Lite/{time_strap}')
    for mmdb in mmdb_data_type:
        url = URLs[mmdb]
        sha256hash = SHA256[mmdb]

        if time_strap is None:
            raise Exception(
                '参数错误，时间戳不能为空，否则asn数据库，地区数据库以及城市数据库将会下载到三个不同的文件夹下，造成读取错误。')

        # 首先下载哈希值
        os.makedirs(dst, exist_ok=True)  # 创建文件夹保存

        print(f'正在下载{mmdb}.sha256哈希校验文件...')
        download_url_to_file(sha256hash, f"{dst}/{mmdb}.sha256", user_agent=_UA)
        try:
            with open(f"{dst}/{mmdb}.sha256", 'r') as fp:
                _sha256_prefix, _name = fp.read().strip().split('  ')
        except Exception as e:
            raise Exception(f'未知错误，大概率是哈希文件读取错误，{e}')  # RE-raise

        print(f'正在下载{mmdb}实际数据库文件...')
        download_url_to_file(url, f'{dst}/{_name}', hash_prefix=_sha256_prefix, user_agent=_UA)
    return dst


if __name__ == '__main__':
    print(download_mmdb('asn', time_strap=time.time()))
