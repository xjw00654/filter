# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import typing

from .whois_query import _api_query

# 请前往http://my.chinaz.com/ChinazAPI/Statistics/AccessStatistics开通自己的key，免费100条
ICP_API_KEY = 'e761b1c6f4e14b78ba9d2b9bc1f9e3a4'
API_URL = f'https://apidatav2.chinaz.com/single/newicp?key={ICP_API_KEY}&domain='


def icp_api_query(
        domain_name: str
) -> typing.Union[dict, None]:
    return _api_query(
        API_URL + domain_name,
        domain_name,
        ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
           'AppleWebKit/537.36 (KHTML, like Gecko) ' \
           'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
    )


if __name__ == '__main__':
    print(icp_api_query('jwxie.cn'))
