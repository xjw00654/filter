# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com


import typing


def exception(caller: typing.Callable, inp: typing.Any, res: typing.Any) -> bool:
    assert res == caller(inp)
    return True
