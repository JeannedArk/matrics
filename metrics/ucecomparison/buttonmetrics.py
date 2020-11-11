# -*- coding: utf-8 -*-
from typing import List, Callable, Union

from aggregationlevel import AggregationLevel
from metrics.filters import filter_interactable_visible_buttons
from metrics.metric import *
from metrics.selectors import selector_widgets_level_uce
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel
from usecaseclassification.usecaseexecution import UseCaseExecution


def selector_widgets(it_unit: Union[UseCaseExecution, BaseExplorationModel], aggregation_lvl):
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is App
        aggregated_widgets = set(widget for state in it_unit.states for widget in state.widgets)
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        aggregated_widgets = selector_widgets_level_uce(it_unit)
    else:
        raise NotImplementedError(f"Not implemented yet for {aggregation_lvl}")

    return aggregated_widgets


def selector_number_of_widgets(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                               filtering_op: Callable,
                               aggregation_lvl) -> List[int]:
    widgets = selector_widgets(it_unit, aggregation_lvl)
    return [len(filtering_op(widgets))]


def button_area(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                filtering_op: Callable,
                aggregation_lvl) -> List[int]:
    widgets = selector_widgets(it_unit, aggregation_lvl)
    areas = []
    for widget in filtering_op(widgets):
        area = widget.visible_boundaries.area()
        assert area >= 0
        areas.append(area)

    return areas


class ButtonButtonsNumberUCE(MultiNumberUCEComparison):
    description = "Number of buttons"
    name = "Quantity of Buttons"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 filtering_widgets=lambda widgets: filter_interactable_visible_buttons(widgets),
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=filtering_widgets,
                         aggregation_lvls=ButtonButtonsNumberUCE.aggregation_lvls,
                         data_select_op=selector_number_of_widgets,
                         outlier_method=outlier_method,
                         plot_config=ButtonButtonsNumberUCE.plot_config)


class ButtonButtonsNumberApp(MultiNumberUCEComparison):
    description = "Number of buttons"
    name = "Quantity of Buttons"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 filtering_widgets=lambda widgets: filter_interactable_visible_buttons(widgets),
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=filtering_widgets,
                         aggregation_lvls=ButtonButtonsNumberApp.aggregation_lvls,
                         data_select_op=selector_number_of_widgets,
                         outlier_method=outlier_method,
                         plot_config=ButtonButtonsNumberUCE.plot_config)


class ButtonAreaUCE(MultiNumberUCEComparison):
    """
    Important: This depends on the screen size!
    """
    description = "Area of buttons"
    name = "Size of Buttons"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)
    use_case_whitelist = [
        "Add_recipe",
        "Search_for_bill_gates",
        "Book_hotel_core",
    ]

    def __init__(self,
                 model,
                 filtering_widgets=lambda widgets: filter_interactable_visible_buttons(widgets),
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=filtering_widgets,
                         aggregation_lvls=ButtonAreaUCE.aggregation_lvls,
                         data_select_op=button_area,
                         outlier_method=outlier_method,
                         plot_config=ButtonAreaUCE.plot_config,
                         use_case_whitelist=ButtonAreaUCE.use_case_whitelist)


class ButtonAreaApp(MultiNumberUCEComparison):
    """
    Important: This depends on the screen size!
    """
    description = "Area of buttons"
    name = "Size of Buttons"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX, axis_type="log")

    def __init__(self,
                 model,
                 filtering_widgets=lambda widgets: filter_interactable_visible_buttons(widgets),
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=filtering_widgets,
                         aggregation_lvls=ButtonAreaApp.aggregation_lvls,
                         data_select_op=button_area,
                         outlier_method=outlier_method,
                         plot_config=ButtonAreaApp.plot_config)
