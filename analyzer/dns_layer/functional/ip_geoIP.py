# coding: utf-8
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


def untar(
        src: str,
        dst: str
) -> None:
    """ 解压缩文件
    :param src: 压缩文件所在位置
    :param dst: 解压缩后的文件所在位置
    :return: None
    """
    import tarfile

    with tarfile.open(src) as tar:
        names = tar.getnames()
        for name in names:
            if name.endswith('.mmdb'):
                tar.extract(name, path=dst)
            else:
                pass


def download_mmdb(
        mmdb_data_type: Union[str, List, Tuple],
        time_strap: float
) -> str:
    """ 根据链接下载city、country、asn号所存储的数据库文件
    :param mmdb_data_type: 所要下载的数据库文件类型，asn、county、city，或是以list的形式给出多个
    :param time_strap: 时间戳，文件保存会以时间戳的形式创建保存在文件夹
    :return: 完整文件路径
    """

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
    if time_strap is None:
        raise Exception(
            '参数错误，时间戳不能为空，否则asn数据库，地区数据库以及城市数据库将会下载到三个不同的文件夹下，造成读取错误。')

    dst = os.path.abspath(f'../../../static_files/GeoIP2-Lite/{time_strap}')
    for mmdb in mmdb_data_type:
        url = URLs[mmdb]
        sha256hash = SHA256[mmdb]

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

        print(f'正在解压{mmdb}实际数据库文件...')
        try:
            untar(f'{dst}/{_name}', dst)
        except Exception as e:
            raise Exception(f"解压错误，解压过程发生错误，请检查{e}")
        else:
            print('正在删除压缩文件...')
            os.remove(f'{dst}/{_name}')  # 未发生错误，删除压缩文件
            os.remove(f'{dst}/{mmdb}.sha256')  # 未发生错误，删除压缩文件
    return dst


class Client:
    def __init__(self, download_new_mmdb_file: bool = False, force: bool = False):
        dst_path = '../../../static_files/GeoIP2-Lite'
        if not download_new_mmdb_file and (not os.path.exists(dst_path) or len(os.listdir(dst_path)) == 0):
            # 不要下载，但是却没有找到数据库文件
            print('当前没有找到任何下载完成的数据库文件，将会自动进行下载，请确保网络通常')
            download_new_mmdb_file = True
        elif not download_new_mmdb_file and (not os.path.exists(dst_path) or len(os.listdir(dst_path)) != 0):
            # 不要下载，且已找到了
            download_new_mmdb_file = False
        elif download_new_mmdb_file:  # 要下载
            if os.path.exists(dst_path) and len(os.listdir(dst_path)) != 0:
                # 已经有一些一下载的东西了，检查一下日期，小于一天，且根据force字段的值判断是否真的要下载
                fresh_downloaded_time = sorted(os.listdir('../../../static_files/GeoIP2-Lite'))[-1]
                if time.time() - float(fresh_downloaded_time) < 86400:
                    if not force:
                        print('距离上一次更新数据库时间小于1天，请尽可能减小更新频率，如果需要强制更新，请使用force=True')
                        download_new_mmdb_file = False
                    else:
                        print('距离上一次更新数据库时间小于1天，将会进行强制数据库更新')
                        download_new_mmdb_file = True  # 显示写出来，便于理解
                else:
                    download_new_mmdb_file = True  # 显示写出来，便于理解
        else:
            raise Exception('逻辑错误，好像你遇到了一些我没有考虑到的事情.... by:jwxie :D')

        if download_new_mmdb_file:
            _folder = download_mmdb(['asn', 'city', 'country'], time_strap=time.time())
        else:
            _folder = os.path.join(dst_path, sorted(os.listdir(dst_path))[-1])

        import geoip2.database

        date = os.listdir(_folder)[0].split('_')[-1]
        self.city_reader = geoip2.database.Reader(f"{_folder}/GeoLite2-City_{date}/GeoLite2-City.mmdb")
        self.asn_reader = geoip2.database.Reader(f"{_folder}/GeoLite2-ASN_{date}/GeoLite2-ASN.mmdb")
        self.country_reader = geoip2.database.Reader(f"{_folder}/GeoLite2-Country_{date}/GeoLite2-Country.mmdb")

    def query_asn(self, ip: Union[List, str]):
        res = []
        if isinstance(ip, str):
            ip = [ip]
        for elem in ip:
            try:
                response = self.country_reader.asn(elem)
                res.append({
                    'ip': elem,
                    'asn': response.autonomous_system_number,
                    'asn_organization': response.autonomous_system_organization
                })
            except Exception as e:
                res.append({
                    'ip': elem,
                    'asn': e.__str__(),
                    'asn_organization': e.__str__(),
                })

        return res

    def query_country(self, ip: Union[List, str]):
        res = []
        if isinstance(ip, str):
            ip = [ip]
        for elem in ip:
            try:
                response = self.country_reader.country(elem)
                res.append({
                    'ip': elem,
                    'country_iso_code': response.country.iso_code,
                    'country_geoname_id': response.country.geoname_id,
                    'country_name': response.country.name,
                    'continent_code': response.continent.code,
                    'continent_geoname_id': response.continent.geoname_id,
                    'continent_name': response.continent.name,
                })
            except Exception as e:
                res.append({
                    'ip': elem,
                    'country_iso_code': e.__str__(),
                    'country_geoname_id': e.__str__(),
                    'country_name': e.__str__(),
                    'continent_code': e.__str__(),
                    'continent_geoname_id': e.__str__(),
                    'continent_name': e.__str__(),
                })
        return res

    def query_city(self, ip: Union[List, str]):
        res = []
        if isinstance(ip, str):
            ip = [ip]

        for elem in ip:
            try:
                response = self.city_reader.city(elem)
                res.append({
                    'ip': elem,
                    'city_name': response.city.name,
                    'city_geoname_id': response.city.geoname_id,
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                })
            except Exception as e:
                res.append({
                    'ip': elem,
                    'city_name': e.__str__(),
                    'city_geoname_id': e.__str__(),
                    'latitude': e.__str__(),
                    'longitude': e.__str__(),
                })
        return res

    def query_all(self, ip: Union[List, str]):
        if isinstance(ip, str):
            ip = [ip]

        city_results = self.query_city(ip)
        country_results = self.query_country(ip)
        asn_results = self.query_asn(ip)

        assert len(city_results) == len(asn_results) == len(country_results)
        return [{**city, **country, **asn} for city, country, asn in zip(city_results, country_results, asn_results)]


if __name__ == '__main__':
    Client(False).query_city('114.43.142.21')
