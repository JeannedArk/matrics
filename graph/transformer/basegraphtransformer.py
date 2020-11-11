# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseGraphTransformer(metaclass=ABCMeta):
    @abstractmethod
    def transform(self):
        pass
