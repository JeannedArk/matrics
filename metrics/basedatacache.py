# -*- coding: utf-8 -*-
import os
import pickle
from abc import abstractmethod, ABCMeta, ABC
from typing import Any, List

from metrics.datacompound import DataCompound
from util import configutil


class BaseDataCache(metaclass=ABCMeta):
    """
    TODO think about to improve the class hierarchy with BaseDataCache:
    ModelAccessor implement BaseDataCache?
    """

    @abstractmethod
    def compute_data(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def get_cache_load_id(self) -> str:
        pass

    def store_data(self, data, file) -> None:
        with open(file, 'wb') as f:
            pickle.dump(data, f)

    def force_reload_data(self, *args, **kwargs):
        load_id = self.get_cache_load_id()
        assert load_id is not None and load_id != "", f"Load id was: {load_id}"
        file = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, load_id)

        if os.path.isfile(file):
            with open(file, 'rb') as fp:
                data = pickle.load(fp)
        else:
            data = self.compute_data(*args, **kwargs)
            if configutil.MATRICS_CACHE_DUMP:
                self.store_data(data, file)
        return data

    def load_data(self, *args, **kwargs):
        load_id = self.get_cache_load_id()
        assert load_id is not None and load_id != "", f"Load id was: {load_id}"
        file = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, load_id)

        if os.path.isfile(file) and configutil.MATRICS_CACHE_READ:
            with open(file, 'rb') as fp:
                data = pickle.load(fp)
        else:
            data = self.compute_data(*args, **kwargs)
            if configutil.MATRICS_CACHE_DUMP:
                self.store_data(data, file)
        return data


# class DataCacheDataCompounds(BaseDataCache, ABC):
#     def store_data(self, data: List[DataCompound], file) -> None:
#         with open(file, 'wb') as f:
#             pickle.dump(data, f)
#
#     def load_data(self, *args, **kwargs) -> List[DataCompound]:
#         load_id = self.get_cache_load_id()
#         assert load_id is not None and load_id != "", f"Load id was: {load_id}"
#         file = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, load_id)
#
#         if os.path.isfile(file) and configutil.MATRICS_CACHE_READ:
#             with open(file, 'rb') as fp:
#                 data: List[DataCompound] = pickle.load(fp)
#         else:
#             data: List[DataCompound] = self.compute_data(*args, **kwargs)
#             if configutil.MATRICS_CACHE_DUMP:
#                 self.store_data(data, file)
#         return data
