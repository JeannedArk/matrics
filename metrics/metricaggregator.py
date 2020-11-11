# -*- coding: utf-8 -*-
from abc import ABC
from collections import Callable

from metrics.metric import *


class MetricAggregator(ModelAccessor, ABC):
    def __init__(self,
                 name: str,
                 model,
                 filtering_op: Callable,
                 data_op: Callable,
                 data_select_op: Callable,
                 aggregation_lvls,
                 description: str,
                 outlier_method):
        """
        :param model: TODO
        :param filtering_op: function to filter for objects that are generated from data_select_op,
        e.g. only interactable widgets
        :param data_select_op: TODO
        :param data_op: determines the data operation on the data frame, e.g. max or mean
        :param aggregation_lvls: the aggregation levels
        :param description: the description that will be displayed in the result plot
        """
        super().__init__(model)
        self.metrics = []
        for aggregation_lvl in aggregation_lvls:
            for it_aggregation_lvl in aggregation_lvl.iter_metric(model):
                try:
                    metric = SingleNumberMetric(name,
                                                model,
                                                filtering_op,
                                                data_op,
                                                data_select_op,
                                                it_aggregation_lvl,
                                                description,
                                                outlier_method)
                    self.metrics.append(metric)
                except MetricsConstructionException as e:
                    print(f"Failed to create SingleNumberMetric in {self.get_id()}, "
                          f"it_aggregation_lvl={it_aggregation_lvl.title()}) with '{e}'.")

    def plot(self):
        return [self.metrics[i].plot(f"{self.get_ui_id()}-{i}") for i in range(len(self.metrics))]

    def get_data_compounds(self):
        return []


class MetricAggregatorAllData(ModelAccessor, ABC):
    def __init__(self,
                 name: str,
                 model,
                 filtering_op: Callable,
                 data_select_op: Callable,
                 aggregation_lvls,
                 description: str,
                 outlier_method):
        """
        :param model: TODO
        :param filtering_op: function to filter for objects that are generated from data_select_op,
        e.g. only interactable widgets
        :param data_select_op: TODO
        :param aggregation_lvls: the aggregation levels
        :param description: the description that will be displayed in the result plot
        """
        super().__init__(model)
        self.metrics = []
        for aggregation_lvl in aggregation_lvls:
            for it_aggregation_lvl in aggregation_lvl.iter_metric(model):
                try:
                    metric = MultiNumberMetric(name,
                                               model,
                                               filtering_op,
                                               data_select_op,
                                               it_aggregation_lvl,
                                               description,
                                               outlier_method)
                    self.metrics.append(metric)
                except MetricsConstructionException as e:
                    print(f"Failed to create MultiNumberMetric in {self.get_id()}, "
                          f"it_aggregation_lvl={it_aggregation_lvl.title()}) with '{e}'.")

    def plot(self):
        return [self.metrics[i].plot(f"{self.get_ui_id()}-{i}") for i in range(len(self.metrics))]

    def get_data_compounds(self):
        return []
