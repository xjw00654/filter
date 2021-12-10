#!/usr/bin/python

import pickle
import typing

import numpy as np

from . import gib_detect_train


class Client:
    def __init__(self):
        model_data = pickle.load(open('../../../static_files/gib_model.pki', 'rb'))
        self.threshold = model_data['thresh']
        self.model_mat = model_data['mat']

    def query(
            self,
            string: str,
            with_prob: bool = True
    ) -> typing.Union[bool, typing.Tuple[bool, float]]:
        prob = gib_detect_train.avg_transition_prob(string, self.model_mat)

        if with_prob:
            return prob > self.threshold, prob
        else:
            return prob > self.threshold

    def query_batch(
            self,
            string: typing.Union[typing.List, typing.Tuple, np.ndarray],
            with_prob: bool = True
    ) -> typing.List:
        pass
