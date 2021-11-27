# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

from typing import Union, List, Dict


def domain_name_seperator(
        domain_name: str,
        sep: str = '.',
        return_struct: bool = False
) -> Union[List[str], Dict[int, str]]:
    """ 给定域名返回分隔后的域名，sep为分隔符号，默认为'.'
    :param domain_name:
    :param sep: 域名的实际分隔符号，如'a.b.c.d'，使用sep='.'分隔，会得到['a', 'b', 'c', 'd']
    :param return_struct: 是否需要按照顶级、次顶级... 的形式以字典给出结果，其中字典的KV顺序为1，2...
    :return: 根据是否返回结构化返回List[str] 或者 Dict[str, str]
    """
    seps = domain_name.split(sep)
    if return_struct:
        return {len(seps) - i: v for i, v in enumerate(seps)}
    else:
        return seps
