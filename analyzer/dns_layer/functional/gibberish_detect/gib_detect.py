#!/usr/bin/python

import os
import pickle
import typing

import numpy as np
from numba import jit

from . import gib_detect_train


class Client:
    def __init__(self):
        base_path = 'static_files/gib_model.pki'
        if os.path.abspath('.').endswith('functional'):
            base_path = '../../../' + base_path
        model_data = pickle.load(open(base_path, 'rb'))

        self.threshold = model_data['thresh']
        self.model_mat = model_data['mat']

    @jit
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
