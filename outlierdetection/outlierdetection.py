# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List


class OutlierDetector(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def outliers(self) -> List:
        pass
