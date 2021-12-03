# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import math
import typing
from collections import Counter

from numba import jit


@jit
def cal_entropy_batch(
        string_batch: typing.Union[typing.List, typing.Tuple],
        do_length_normalization: bool = False,
        except_dot: bool = False
) -> list:
    """
    计算一个批次中所有数据的熵值

    :param string_batch: 一批次字符串数据，需要一个list或者tuple
    :param do_length_normalization: 是否需要做域名长度归一化
    :param except_dot: 是否需要将字符数据中的'.'纳入熵值计算
    :return: 该批次数据中每一个数据的熵值
    """

    entropys = []
    if isinstance(string_batch, list) or isinstance(string_batch, tuple):
        for _string in string_batch:
            entropys.append(cal_entropy(_string, do_length_normalization, except_dot))
    else:
        raise Exception('格式错误，整批次的字符串进行熵值计算需要一个list或者tuple')

    return entropys


def cal_entropy_group(
        string_group: typing.Union[typing.List, typing.Tuple, str],
        do_length_normalization: bool = False,
        except_dot: bool = False
) -> float:
    """
    对于整组的字符串数据进行熵值计算，返回一个整体的熵值

    :param string_group: 字符串组合，需要一个list或者tuple，或者是已经整合成一个的str[不需要使用间隔符]
    :param do_length_normalization: 是否需要做域名长度归一化
    :param except_dot: 是否需要将字符串中的'.'纳入熵值计算
    :return: 该组字符串数据的熵值
    """
    if isinstance(string_group, list) or isinstance(string_group, tuple):
        return cal_entropy("".join(string_group), do_length_normalization, except_dot)
    elif isinstance(string_group, str):
        return cal_entropy(string_group, do_length_normalization, except_dot)
    else:
        raise Exception('格式错误，整组的字符串数据进行熵值计算需要一个list或者tuple，或者是已经整合成一个的str')


def cal_entropy(
        string: str,
        do_length_normalization: bool = False,
        except_dot: bool = False
) -> float:
    """
    计算单个字符串的熵值

    :param string: 给定的单个字符串
    :param do_length_normalization: 是否需要做字符串长度归一化
    :param except_dot: 是否需要将字符串中的'.'纳入熵值计算
    :return: 该字符串的熵值
    """
    entropy = 0.0
    if except_dot:
        string = string.replace('.', '')

    ct = Counter(string)
    _length = len(string)

    for (k, v) in ct.items():
        p = float(v) / float(_length)
        entropy -= p * math.log(p, 2)

    if do_length_normalization:
        entropy /= _length
    return entropy


if __name__ == '__main__':
    print(cal_entropy('baidu.com'))
