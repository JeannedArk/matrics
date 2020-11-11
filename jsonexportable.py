# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class JsonExportable(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self) -> str:
        pass
