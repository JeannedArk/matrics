# -*- coding: utf-8 -*-
from collections import Callable
from typing import List, Union

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector
from usecaseclassification.usecaseexecution import UseCaseExecution


def selector_number_of_distinct_features(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                                         filtering_entries: Callable,
                                         aggregation_lvl) -> List[int]:
    features = []
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is App
        features = [feature for state in it_unit.states for feature in state.features]
    elif aggregation_lvl == AggregationLevel.STATE:
        # it_unit is App
        features = [state.features for state in it_unit.states]
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        trace_view = it_unit.get_representative_trace_view()
        features = trace_view.get_features()
    else:
        raise NotImplementedError(f"Not implemented yet for {aggregation_lvl}")

    # Put features in a set to remove duplicates
    return [len(filtering_entries(set(features)))]


class FeatureNumber(MultiNumberUCEComparison):
    description = "Number of distinct features"
    name = "Quantity of Features"
    # TODO STATE
    aggregation_lvls = [AggregationLevel.APP, AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=FeatureNumber.aggregation_lvls,
                         data_select_op=selector_number_of_distinct_features,
                         outlier_method=outlier_method,
                         plot_config=FeatureNumber.plot_config)
