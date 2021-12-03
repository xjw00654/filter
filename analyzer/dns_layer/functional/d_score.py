# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

"""
根据经纬度计算两点间Dscore值，使用函数d_score
"""

import math


def d_score(
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
) -> float:
    """
    利用HaversineRAD，计算两个点（经纬度）之间的欧氏距离

    :param lng1: 第一个点的纬度
    :param lat1: 第一个点的经度
    :param lng2: 第二个点的经度
    :param lat2: 第二个点的经度
    :return: 两点之间的欧氏距离，浮点数
    """
    lng1, lat1, lng2, lat2 = map(math.radians, [float(lng1), float(lat1), float(lng2), float(lat2)])

    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    distance = 2 * math.asin(math.sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    return distance


def d_score_fast(
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
) -> float:
    """
    利用简化方法，牺牲一定精度快速计算两个点（经纬度）之间的欧氏距离，
    大约比高精度版快一倍

    :param lng1: 第一个点的纬度
    :param lat1: 第一个点的经度
    :param lng2: 第二个点的经度
    :param lat2: 第二个点的经度
    :return: 两点之间的欧氏距离，浮点数
    """
    dx = lng1 - lng2
    dy = lat1 - lat2
    avg_lat = lat1 / 2. + lat2 / 2.

    lx = math.radians(dx) * 6367000.0 * math.cos(math.radians(avg_lat))
    ly = math.radians(dy) * 6367000.0
    distance = math.sqrt(lx ** 2 + ly ** 2)
    return distance


if __name__ == '__main__':
    import time

    s = time.time()
    for _ in range(round(1e7)):
        d_score(39.941, 116.45, 39.94, 116.451, )
    print(time.time() - s)
    s = time.time()
    for _ in range(round(1e7)):
        d_score_fast(39.941, 116.45, 39.94, 116.451, )
    print(time.time() - s)
