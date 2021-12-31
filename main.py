# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com
import itertools
import pickle

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

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

    data_1gram, vocab_freq = nlp.cal_ngram(data=data, n=1, with_vocab_freq=True)
    data_entropy = F.cal_entropy_batch(data, do_length_normalization=False, except_dot=False)
    data_gibberish = [gibberish_client.query(e)[1] for e in data]
    data_freq = nlp.cal_freq(data)

    ngram_len = vocab_freq[1].indices.shape[0] * 1.
    rr = np.array(list(map(np.mean, data_1gram))) / ngram_len, np.array(
        list(map(np.std, data_1gram))) / ngram_len, data_entropy, data_gibberish, data_freq
    return np.hstack([np.stack([rr[0], rr[1], rr[2], rr[3]]).transpose((1, 0)), np.array(rr[4])]), label, sub_label


class DS(Dataset):
    def __init__(self, data, label):
        self.data = data
        self.label = label

    def __getitem__(self, idx):
        return torch.from_numpy(self.data[idx, :]).float(), \
               torch.from_numpy(np.array(self.label[idx], dtype=np.int8)).long()

    def __len__(self):
        return self.data.shape[0]


class Model(torch.nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.m = torch.nn.ModuleList([
            torch.nn.Linear(10, 32),
            torch.nn.Linear(32, 16),
            torch.nn.Linear(16, 2),
        ])

    def forward(self, x):
        for e in self.m:
            x = e(x)
        return x


if __name__ == '__main__':
    # data = dga_analysis()

    fs = pickle.load(open('fs.pkl', 'rb'))
    lb = pickle.load(open('lb.pkl', 'rb'))

    X_train, X_test, y_train, y_test = train_test_split(fs, lb[:, 0], test_size=0.2, random_state=7010)

    train_data = DataLoader(DS(X_train, y_train), batch_size=1024)
    test_data = DataLoader(DS(X_test, y_test), batch_size=1024)

    M = Model()
    # M.cuda()
    loss = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(M.parameters(), lr=0.01)

    epoch_acc = []
    for epoch in range(1, 6):
        train_loss = []
        test_acc = []

        M.train()
        for i, (data, target) in enumerate(train_data):
            # data = data.cuda()
            # target = target.cuda()
            optimizer.zero_grad()
            output = M(data)
            loss_val = loss(output, target)
            loss_val.backward()
            optimizer.step()
            train_loss.append(loss_val.item())
            if i % 100 == 0 and i != 0:
                print('epoch: ', epoch, 'iter: ', i, '/', len(train_data), 'train: ', np.mean(train_loss))
        M.eval()
        for i, (data, target) in enumerate(test_data):
            # data = data.cuda()
            # target = target.cuda()
            output = M(data)
            test_acc.append(((output.argmax(dim=1) == target).sum() / 1024).item())
            if i % 100 == 0 and i != 0:
                print('epoch: ', epoch, 'iter: ', i, '/', len(test_data), 'Accuracy: ', np.mean(test_acc))
        epoch_acc.append(np.max(test_acc))
        torch.save(M, f'model.ep{epoch}.pth')
    print(epoch_acc)
