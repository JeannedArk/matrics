# -*- coding: utf-8 -*-

META_DATA_TRANSITION = 'transition'
META_DATA_ATD = 'atd'


class MetaData(object):
    def __init__(self, data=None):
        self.data = {} if data is None else data

    def get(self, k):
        return self.data[k]

    def put(self, k, v):
        self.data[k] = v

    def has(self, k):
        return k in self.data

    def copy_from_iter(self, _iter):
        return MetaData({i: self.data[i] for i in _iter})

    def merge(self, other_meta_data):
        for k, v in other_meta_data.data.items():
            self.data[k] = v

    def is_empty(self):
        return not bool(self.data)
