# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Set, Optional


class TaggingMethod(Enum):
    DENSITY = "density"
    UCE = "uce"


class BaseStateTagger(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.tag_method: Optional[TaggingMethod] = None

    @abstractmethod
    def tag_states(self, exploration_model) -> Set[str]:
        pass
