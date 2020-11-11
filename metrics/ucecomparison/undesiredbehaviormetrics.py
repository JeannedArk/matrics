# -*- coding: utf-8 -*-
from typing import List, Callable, Union

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel


def selector_crash_number(it_unit: BaseExplorationModel,
                          filtering_entries: Callable,
                          aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        return [sum(1
                    for trace in it_unit.traces
                    for trans in trace.transitions
                    if not trans.successful)]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class UndesiredBehaviorCrashNumber(MultiNumberUCEComparison):
    description = "Number of not successful actions"
    name = "Quantity of Crashes"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=UndesiredBehaviorCrashNumber.aggregation_lvls,
                         data_select_op=selector_crash_number,
                         outlier_method=outlier_method,
                         plot_config=UndesiredBehaviorCrashNumber.plot_config)
