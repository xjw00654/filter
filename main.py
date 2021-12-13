# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import itertools

import analyzer.dns_layer.functional as F
import analyzer.dns_layer.functional.domain_name_nlp_features as nlp


def dga_analysis():
    whitelist_domain_name = nlp.get_whitelist_from_txt(use_v2ray=False)
    dga_domain_names, dga_domain_types = nlp.get_dga_from_txt()
    dga_domain_types, dga_domain_names = list(dga_domain_types), list(dga_domain_names)

    data = [e for e in itertools.chain(whitelist_domain_name, dga_domain_names)]  # 去掉suffix
    label = [0] * len(whitelist_domain_name) + [1] * len(dga_domain_names)
    sub_label = ['normal'] * len(whitelist_domain_name) + dga_domain_types

    # initialize query client
    gibberish_client = F.gibberish_query_client()

    data_1gram = nlp.cal_ngram(data=data, n=1)
    data_entropy = F.cal_entropy_batch(data)
    data_gibberish = [gibberish_client.query(e) for e in data]
    data_vowel = nlp.cal_vowel(data)
    data_freq = nlp.cal_freq(data)

    a = 10


if __name__ == '__main__':
    dga_analysis()
