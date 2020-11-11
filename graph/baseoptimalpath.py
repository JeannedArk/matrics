# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseOptimalPath(metaclass=ABCMeta):
    @abstractmethod
    def find_path(self, nodes_ls, start_node):
        pass
