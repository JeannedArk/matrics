# -*- coding: utf-8 -*-

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.metricaggregator import MetricAggregator, MetricAggregatorAllData
from metrics.selectors import selector_number_of_widgets


class UIInteractableVisibleWidgetsNumber(MetricAggregatorAllData):
    description = "Number of interactable and visible widgets"
    name = "Quantity of GUI Elements"
    aggregation_lvls = [AggregationLevel.STATE]

    def __init__(self,
                 model=None,
                 filtering_widgets=lambda l: [w for w in l if w.is_interactable_and_visible()],
                 description=description,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(name=UIInteractableVisibleWidgetsNumber.name,
                         model=model,
                         filtering_op=filtering_widgets,
                         data_select_op=selector_number_of_widgets,
                         aggregation_lvls=UIInteractableVisibleWidgetsNumber.aggregation_lvls,
                         description=description,
                         outlier_method=outlier_method)
