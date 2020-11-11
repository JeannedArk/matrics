# -*- coding: utf-8 -*-
from json import JSONEncoder


class MultiNumberUCEComparisonDumpEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class DataCompoundEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class DataCompoundDumpEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
