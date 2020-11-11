# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseModelViz(metaclass=ABCMeta):
    def __init__(self, ui_html_id):
        self.ui_html_id = ui_html_id

    @abstractmethod
    def visualize_graph(self):
        pass
