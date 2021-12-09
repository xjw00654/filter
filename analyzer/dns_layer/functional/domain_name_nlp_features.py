# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import os
import typing

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


def _get_specific_ext_files(path: str, ext: str):
    file_list = []
    for root, _, fns in os.walk(path):
        for fn in fns:
            if fn.endswith(ext):
                file_list.append(os.path.join(root, fn))
    return file_list


def get_whitelist_from_txt():
    top1m_path = '../../../static_files/top1m'
    v2ray_rules_path = '../../../static_files/v2ray-rules'
    top1m_txt = [float(e) for e in os.listdir(top1m_path)]
    v2ray_rules_txt = [float(e) for e in os.listdir(v2ray_rules_path)]
    if len(top1m_txt) == 0:
        raise Exception('文件缺失错误，暂时未找到top1m或是v2ray-rules的任何已下载文件')
    else:
        top1m_path = os.path.join(top1m_path, str(top1m_txt[-1]))
        v2ray_rules_path = os.path.join(v2ray_rules_path, str(v2ray_rules_txt[-1]))

    top1m_txt_list = _get_specific_ext_files(top1m_path, ".txt")
    v2ray_rules_txt_list = _get_specific_ext_files(v2ray_rules_path, '.txt')

    whitelist_txt_list = top1m_txt_list + v2ray_rules_txt_list

    wl = []
    for txt in whitelist_txt_list:
        wl += [elem for elem in [e.strip().replace('full:', '') for e in open(txt, 'r', encoding='utf-8').readlines()
                                 if not e.startswith('regexp:')] if len(elem) >= 4]
    return list(set(wl))


def get_features(
        data: list,
        ngram: typing.Union[typing.List, typing.Tuple] = (1,),
        tfidf_feature: bool = True,
) -> dict:
    raw_documents = [e.strip() for e in
                     open('../../../static_files/v2ray-rules/1638241629.8807404/gfw.txt', 'r').readlines()]

    ngram_vectorizer = CountVectorizer(analyzer='char', ngram_range=ngram)
    ngram_vectorizer.fit(raw_documents)
    data_ngram_vector = ngram_vectorizer.transform(data)

    result = {'ngram': data_ngram_vector, }
    if tfidf_feature:
        tfidf_vectorizer = TfidfVectorizer(analyzer='char', ngram_range=ngram)
        tfidf_vectorizer.fit(raw_documents)
        data_tfidf_vector = tfidf_vectorizer.transform(data)
        result['tfidf'] = data_tfidf_vector

    return result


if __name__ == '__main__':
    import re
    import numpy as np
    from collections import Counter
    import pandas as pd

    import matplotlib.pyplot as plt
    import seaborn
    from analyzer.dns_layer.functional.entropy import cal_entropy_batch

    wl = np.array(get_whitelist_from_txt())

    bl = np.array(
        [elem for elem in
         [e.strip().split('\t')[:2] for e in open('../../../static_files/dga.txt', 'r', encoding='utf-8').readlines()
          if not e.startswith('#') and e != "" and e[0] != "\n"] if len(elem[1]) >= 4])
    cls, bl = bl[:, 0], bl[:, 1]

    label_c = Counter(cls)
    label_d = {'normal': len(set(cls)), **{e: i for i, e in enumerate(set(cls))}}
    label_rd = {i: e for i, e in enumerate(set(cls))}

    label = np.array([label_d[e] for e in cls] + [label_d['normal']] * len(wl))

    data = np.append(bl, wl)
    cls = np.append(cls, np.array(['normal'] * len(wl)))
    assert len(data) == len(label)

    # vowel-papers
    bl_counter = [len([c for c in e if c.lower() in 'aeiou']) / len(e) for e in bl]
    wl_counter = [len([c for c in e if c.lower() in 'aeiou']) / len(e) for e in wl]

    plt.close()
    seaborn.distplot(bl_counter, color='g')
    seaborn.distplot(wl_counter, color='orange')
    plt.savefig(f'../../../static_files/vowel_kde.png')

    # ngram-papers
    for n in range(3, 4):
        bl_unigram_vectorizer = CountVectorizer(analyzer='char', ngram_range=(n, n))
        bl_unigram_vectorizer.fit(bl.tolist())
        bl_vocab = bl_unigram_vectorizer.vocabulary_

        bl_vocab_sum = sum(bl_vocab.values())
        bl_unigram_freq_avg = [np.mean([bl_vocab[elem.lower()]
                                        for elem in re.findall(".{" + str(n) + "}", e)]).tolist() for e in bl]
        bl_unigram_freq_std = [np.std([bl_vocab[elem.lower()]
                                       for elem in re.findall(".{" + str(n) + "}", e)]).tolist() for e in bl]

        wl_unigram_vectorizer = CountVectorizer(analyzer='char', ngram_range=(n, n))
        wl_unigram_vectorizer.fit(wl.tolist())
        wl_vocab = wl_unigram_vectorizer.vocabulary_

        wl_vocab_sum = sum(wl_vocab.values())
        wl_unigram_freq_avg = [np.mean([wl_vocab[elem.lower()]
                                        for elem in re.findall(".{" + str(n) + "}", e)]).tolist() for e in wl]
        wl_unigram_freq_std = [np.std([wl_vocab[elem.lower()]
                                       for elem in re.findall(".{" + str(n) + "}", e)]).tolist() for e in wl]

        plt.close()
        seaborn.distplot(wl_unigram_freq_avg, color='g')
        seaborn.distplot(bl_unigram_freq_avg, color='orange')
        plt.savefig(f'../../../static_files/_{n}gram_kde_avg.png')

        plt.close()
        seaborn.distplot(wl_unigram_freq_std, color='g')
        seaborn.distplot(bl_unigram_freq_std, color='orange')
        plt.savefig(f'../../../static_files/_{n}gram_kde_std.png')

    # entropy boxplot
    data_entropy = cal_entropy_batch(data)
    df = pd.DataFrame(list(zip(data_entropy, cls)), columns=['entropy', 'label'])
    plt.figure(figsize=(10, 30))
    seaborn.boxplot(y='label', x='entropy', data=df, orient="h")
    plt.savefig('../../../static_files/entropy.png')

    print(get_features(data=['jwxie.cn', ], ngram=(1, 2,), tfidf_feature=True))
