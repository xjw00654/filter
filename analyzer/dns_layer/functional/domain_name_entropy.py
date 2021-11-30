# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import math
import typing
from collections import Counter

from numba import jit


@jit
def cal_entropy_batch(
        domain_name_batch: typing.Union[typing.List, typing.Tuple],
        do_length_normalization: bool = False,
        except_dot: bool = False
) -> list:
    """
    计算一个批次中所有域名的熵值

    :param domain_name_batch: 一批次域名数据，需要一个list或者tuple
    :param do_length_normalization: 是否需要做域名长度归一化
    :param except_dot: 是否需要将域名中的'.'纳入熵值计算
    :return: 该批次域名中每一个域名的熵值
    """

    entropys = []
    if isinstance(domain_name_batch, list) or isinstance(domain_name_batch, tuple):
        for domain_name in domain_name_batch:
            entropys.append(cal_entropy(domain_name, do_length_normalization, except_dot))
    else:
        raise Exception('格式错误，整批次的域名进行熵值计算需要一个list或者tuple')

    return entropys


def cal_entropy_group(
        domain_name_group: typing.Union[typing.List, typing.Tuple, str],
        do_length_normalization: bool = False,
        except_dot: bool = False
) -> float:
    """
    对于整组的域名进行熵值计算，返回一个整体的熵值

    :param domain_name_group: 域名组合，需要一个list或者tuple，或者是已经整合成一个的str[不需要使用间隔符]
    :param do_length_normalization: 是否需要做域名长度归一化
    :param except_dot: 是否需要将域名中的'.'纳入熵值计算
    :return: 该组域名的熵值
    """
    if isinstance(domain_name_group, list) or isinstance(domain_name_group, tuple):
        return cal_entropy("".join(domain_name_group), do_length_normalization, except_dot)
    elif isinstance(domain_name_group, str):
        return cal_entropy(domain_name_group, do_length_normalization, except_dot)
    else:
        raise Exception('格式错误，整组的域名进行熵值计算需要一个list或者tuple，或者是已经整合成一个的str')


def cal_entropy(domain_name: str, do_length_normalization: bool = False, except_dot: bool = False) -> float:
    """
    计算单个域名熵值

    :param domain_name: 给定的单个域名
    :param do_length_normalization: 是否需要做域名长度归一化
    :param except_dot: 是否需要将域名中的'.'纳入熵值计算
    :return: 该域名的熵值
    """
    entropy = 0.0
    if except_dot:
        domain_name = domain_name.replace('.', '')

    ct = Counter(domain_name)
    domain_length = len(domain_name)

    for (k, v) in ct.items():
        p = float(v) / float(domain_length)
        entropy -= p * math.log(p, 2)

    if do_length_normalization:
        entropy /= domain_length
    return entropy


if __name__ == '__main__':
    print(cal_entropy('baidu.com'))
