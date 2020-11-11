# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseCriterion(metaclass=ABCMeta):
    @abstractmethod
    def decide(self, *args, **kwargs):
        pass
