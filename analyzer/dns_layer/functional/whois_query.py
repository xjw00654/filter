# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import os
import re
import time
import typing

import requests

# 请前往http://my.chinaz.com/ChinazAPI/Statistics/AccessStatistics开通自己的key，免费100条
WHOIS_API_KEY = '8582b25b14a54ac18550ad3b61fd3df7'
API_URL = f'https://apidatav2.chinaz.com/single/whois?key={WHOIS_API_KEY}&domain='
ASYNC_API_STATUS_URL = 'https://apidatav2.chinaz.com/batch/apiresut'

_RE = re.compile("^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$")


def _is_valid_domain_name(
        domain_name: str
) -> bool:
    """
    判断是否是正常的域名

    :param domain_name: 需要验证的域名
    :return:
    """
    return bool(re.search(_RE, domain_name))


def _api_query_batch_async(
        api_url: str,
        domain_names: list,
        _n_per_query: int = 5,
        ua: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
) -> typing.Union[None, dict]:
    """
    异步任务分发，将给定的域名以batch的形式异步提交到API接口内，返回任务的ID号

    :param api_url: 请求url地址
    :param domain_names: 提交的域名列表
    :param _n_per_query: 每次请求的数量，要求小于等于50
    :param ua: UA值
    :return: 字典形式的返回，K为API接口返回的任务id号，V为该任务内的请求域名数量
    """
    task_stamp = time.strftime("%Y%m%d-%H-%M-%S", time.localtime())
    if _n_per_query > 50:
        raise Exception('参数错误，每次请求的数量不能超过50个域名')

    results = {}
    for idx, i in enumerate(range(0, len(domain_names), _n_per_query)):
        dn_no_combine = domain_names[i * _n_per_query: min((i + 1) * _n_per_query, len(domain_names))]
        dn = "|".join(dn_no_combine)

        try:
            task_id_response = requests.get(api_url + dn, headers={'User-Agent': ua})
            if not task_id_response or task_id_response.json()['StateCode'] != 1:
                raise Exception('请求错误，网络错误或者请求不成功')
            else:
                response_content = task_id_response.json()
                results[response_content['TaskID']] = {'Total': response_content['Total'], }
        except Exception as e:
            print(e)
            with open(f'whois_batch_query_failed_domain_names_{task_stamp}.txt', 'a+') as fp:
                for _e in [e for e in dn.split('|') if e]:
                    fp.write(_e + '\n')
            print(f"第{idx}组任务的{len([e for e in dn.split('|') if e])}发放失败，查询失败的域名会记录在"
                  f"{os.path.abspath('./whois_batch_query_failed_domain_names_[当前时间].txt')}文件内")

    print(f'所有的请求结束，当前的所有任务ID号为:{results}')
    if len(results.keys()):
        return None
    else:
        return results


def _api_query(
        api_url: str,
        domain_name: str,
        ua: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
) -> typing.Union[dict, None]:
    """
    api的提交接口

    :param api_url: 请求的url地址
    :param domain_name: 域名值
    :param ua: UA值
    :return: 正确返回字典，错误返回None
    """

    if not _is_valid_domain_name(domain_name):
        return {'Host': domain_name, 'msg': f'查询失败，给定的域名不符合域名规则（注意不要带上协议头）'}
    else:
        api_response = requests.get(api_url + domain_name, headers={'User-Agent': ua})
        if api_response:
            return api_response.json()['Result']
        else:
            return {'Host': domain_name, 'msg': f'查询失败，错误码:{api_response.status_code}'}


def whois_api_query_batch_async(
        domain_names: list,
        _n_per_query: int = 5,
) -> typing.Union[None, dict]:
    """
    whois批量查询的异步接口

    :param domain_names: 域名列表
    :param _n_per_query: 每次请求的域名数量，最大不超过50，默认为5
    :return: 正确返回字典，错误返回None
    """
    return _api_query_batch_async(
        API_URL.replace('single', 'batch'),
        domain_names,
        _n_per_query=5,
        ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
           'AppleWebKit/537.36 (KHTML, like Gecko) ' \
           'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
    )


def whois_api_query(
        domain_name: str
) -> typing.Union[dict, None]:
    """
    whois单条域名查询接口

    :param domain_name: 需要查询的域名
    :return: 正常返回字典，错误返回None
    """
    return _api_query(
        API_URL,
        domain_name,
        ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
           'AppleWebKit/537.36 (KHTML, like Gecko) ' \
           'Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'
    )


if __name__ == '__main__':
    print(whois_api_query_batch_async(['jwxie.com', ]))
