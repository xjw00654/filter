# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import typing

from numba import jit


@jit
def cal_length_batch(
        domain_name_batch: typing.Union[typing.List, typing.Tuple],
        except_dot: bool = False
) -> list:
    """ 计算一个批次中所有域名的长度
    :param domain_name_batch: 一批次域名数据，需要一个list或者tuple
    :param except_dot: 是否需要将域名中的'.'纳入长度计算
    :return: 该批次域名中每一个域名的长度
    """

    entropys = []
    if isinstance(domain_name_batch, list) or isinstance(domain_name_batch, tuple):
        for domain_name in domain_name_batch:
            entropys.append(cal_length(domain_name, except_dot))
    else:
        raise Exception('格式错误，整批次的域名进行长度计算需要一个list或者tuple')

    return entropys


def cal_length_group(
        domain_name_group: typing.Union[typing.List, typing.Tuple, str],
        except_dot: bool = False
) -> int:
    """ 对于整组的域名进行长度计算，返回一个整体的长度
    :param domain_name_group: 域名组合，需要一个list或者tuple，或者是已经整合成一个的str[不需要使用间隔符]
    :param except_dot: 是否需要将域名中的'.'纳入长度计算
    :return: 该组域名的长度
    """
    if isinstance(domain_name_group, list) or isinstance(domain_name_group, tuple):
        return cal_length("".join(domain_name_group), except_dot)
    elif isinstance(domain_name_group, str):
        return cal_length(domain_name_group, except_dot)
    else:
        raise Exception('格式错误，整组的域名进行长度计算需要一个list或者tuple，或者是已经整合成一个的str')


def cal_length(domain_name: str, except_dot: bool = False) -> int:
    """ 计算单个域名长度
    :param domain_name: 给定的单个域名
    :param except_dot: 是否需要将域名中的'.'纳入长度计算
    :return: 该域名的长度
    """
    if except_dot:
        domain_name = domain_name.replace('.', '')

    return len(domain_name)


if __name__ == '__main__':
    print(cal_length('baidu.com'))
