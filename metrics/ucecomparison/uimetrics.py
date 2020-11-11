# -*- coding: utf-8 -*-
from typing import Union, Callable, List, Set

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from metrics.ucecomparison.networkmetrics import NetworkRequestsNumberUCE
from model.baseexplorationmodel import BaseExplorationModel
from model.widget import Widget
from usecaseclassification.usecaseexecution import UseCaseExecution


def selector_widgets_level_uce(uce: UseCaseExecution) -> Set[Widget]:
    trace_view = uce.get_representative_trace_view()
    aggregated_widgets = set(widget
                             for trans in trace_view.get_transitions()
                             for widget in trans.source_state_o.widgets)

    return aggregated_widgets


def selector_widgets(it_unit: Union[UseCaseExecution, BaseExplorationModel], aggregation_lvl):
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is App
        aggregated_widgets = [set(widget for state in it_unit.states for widget in state.widgets)]
    elif aggregation_lvl == AggregationLevel.STATE:
        # it_unit is App
        aggregated_widgets = [set(state.widgets) for state in it_unit.states]
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        aggregated_widgets = [selector_widgets_level_uce(it_unit)]
    else:
        raise NotImplementedError(f"Not implemented yet for {aggregation_lvl}")

    return aggregated_widgets


def selector_number_of_widgets(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                               filtering_widgets: Callable,
                               aggregation_lvl) -> List[int]:
    aggregated_widgets = selector_widgets(it_unit, aggregation_lvl)
    return [len(filtering_widgets(widgets)) for widgets in aggregated_widgets]


class UIInteractableVisibleWidgetsNumber(MultiNumberUCEComparison):
    description = "Number of interactable and visible widgets"
    name = "Quantity of GUI Elements"
    aggregation_lvls = [AggregationLevel.APP, AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model=None,
                 filtering_widgets=lambda l: [w for w in l if w.is_interactable_and_visible()],
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=filtering_widgets,
                         aggregation_lvls=NetworkRequestsNumberUCE.aggregation_lvls,
                         data_select_op=selector_number_of_widgets,
                         outlier_method=outlier_method,
                         plot_config=UIInteractableVisibleWidgetsNumber.plot_config)
