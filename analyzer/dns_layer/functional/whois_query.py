# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import re
import typing

import requests

# 请前往http://my.chinaz.com/ChinazAPI/Statistics/AccessStatistics开通自己的key，免费100条
WHOIS_API_KEY = '8582b25b14a54ac18550ad3b61fd3df7'
API_URL = f'https://apidatav2.chinaz.com/single/whois?key={WHOIS_API_KEY}&domain='

_RE = re.compile("^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$")


def _is_valid_domain_name(
        domain_name: str
) -> bool:
    return bool(re.search(_RE, domain_name))


def _api_query(
        api_url: str,
        domain_name: str,
        ua: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
) -> typing.Union[dict, None]:
    if not _is_valid_domain_name(domain_name):
        return {'Host': domain_name, 'msg': f'查询失败，给定的域名不符合域名规则（注意不要带上协议头）'}
    else:
        api_response = requests.get(api_url, headers={'User-Agent': ua})
        if api_response:
            return api_response.json()['Result']
        else:
            return {'Host': domain_name, 'msg': f'查询失败，错误码:{api_response.status_code}'}


def whois_api_query(
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
    print(whois_api_query('jwxie.com'))
