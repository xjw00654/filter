# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import math
from collections import defaultdict

from tqdm.auto import tqdm


def _build_tfidf_dict():
    # 1.分词，去除停用词
    _file = '../../../static_files/top-1m.csv'
    top1m_domain_names_split = [document.split(',')[1].strip().split('.') for document in open(_file).readlines()]

    # 2.计算词频
    frequency = defaultdict(int)
    # 遍历分词后的结果集，计算每个词出现的频率

    _base_weight = 100
    _step = 100000
    _multiplier = math.pow(_base_weight, 1. / (len(top1m_domain_names_split) // _step))
    for i, dn in tqdm(enumerate(top1m_domain_names_split), total=len(top1m_domain_names_split)):
        _weight = _base_weight / (_multiplier ** (i // _step + 1))
        for token in dn:
            frequency[token] += _weight


if __name__ == '__main__':
    _build_tfidf_dict()
