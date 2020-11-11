# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc

from metrics.datacompound import DataCompound
from util.uiutil import header_metric


class ModelAccessor(metaclass=ABCMeta):
    """
    The model accessor only gets the model. It is the lowest layer of the metric related class
    hierarchy.
    """
    def __init__(self, model):
        self.model = model

    @property
    @classmethod
    @abstractmethod
    def description(cls):
        """
        Enforce the description property to be defined as a class variable for child classes.
        """
        return NotImplementedError

    @abstractmethod
    def get_data_compounds(self) -> List[DataCompound]:
        pass

    @abstractmethod
    def plot(self, *args, **kwargs):
        pass

    @classmethod
    def ui_element(cls, show_header=True):
        assert cls.description is not None
        children = []
        if show_header:
            children.append(header_metric(cls.description))
        children.append(dcc.Loading(id=cls.get_ui_loading_id(), children=[], type="circle"))
        return dbc.Container(children)

    @classmethod
    def get_id(cls) -> str:
        return f"{cls.__module__.lower()}-{cls.__name__.lower()}".replace(".", "-")

    @classmethod
    def get_short_id(cls) -> str:
        return f"{cls.__name__.lower()}".replace(".", "-")

    @classmethod
    def get_ui_id(cls) -> str:
        return f"{cls.get_id()}-id"

    @classmethod
    def get_ui_loading_id(cls) -> str:
        return f"loading-{cls.get_id()}-id"
