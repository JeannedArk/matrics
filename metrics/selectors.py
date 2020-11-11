# -*- coding: utf-8 -*-
from typing import Set, Callable, List

from aggregationlevel import AggregationLevel
from model.widget import Widget
from usecaseclassification.usecaseexecution import UseCaseExecution


def selector_widgets_level_uce(uce: UseCaseExecution) -> Set[Widget]:
    trace_view = uce.get_representative_trace_view()
    aggregated_widgets = set(widget
                             for trans in trace_view.get_transitions()
                             for widget in trans.source_state_o.widgets)

    return aggregated_widgets


def selector_widgets(it_unit, aggregation_lvl):
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is App
        aggregated_widgets = [set(widget for state in it_unit.exploration_model.states for widget in state.widgets)]
    elif aggregation_lvl == AggregationLevel.STATE:
        # it_unit is App
        aggregated_widgets = [set(state.widgets) for state in it_unit.exploration_model.states]
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        aggregated_widgets = [selector_widgets_level_uce(it_unit)]
    else:
        raise NotImplementedError(f"Not implemented yet for {aggregation_lvl}")

    return aggregated_widgets


def selector_number_of_widgets_level_uce(uce: UseCaseExecution, filtering_widgets: Callable) -> int:
    aggregated_widgets = selector_widgets_level_uce(uce)
    return len(filtering_widgets(aggregated_widgets))


def selector_number_of_widgets_level_uce_ls(uce: UseCaseExecution, filtering_widgets: Callable) -> List[int]:
    aggregated_widgets = selector_widgets_level_uce(uce)
    return [len(filtering_widgets(aggregated_widgets))]


def selector_number_of_widgets(filtering_widgets, data_op, it_unit, aggregation_lvl):
    aggregated_widgets = selector_widgets(it_unit, aggregation_lvl)
    return [len(filtering_widgets(widgets)) for widgets in aggregated_widgets]
