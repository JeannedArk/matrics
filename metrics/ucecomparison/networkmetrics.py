# -*- coding: utf-8 -*-
from typing import List, Callable, Union

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel
from model.har import HarEntry
from outlierdetection.univariateoutlierdetection import IQROutlierDetector
from usecaseclassification.usecaseexecution import UseCaseExecution


def selector_network_entries(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                             aggregation_lvl) -> List[HarEntry]:
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is App
        entries = [entry
                   for har in it_unit.hars
                   for entry in har.entries]
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        entries = it_unit.get_representative_trace_view().get_all_network_entries()
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")
    return entries


def selector_number_of_entries(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                               filtering_entries: Callable,
                               aggregation_lvl) -> List[int]:
    entries = selector_network_entries(it_unit, aggregation_lvl)
    return [len(entries)]


# TODO could be wrong
def selector_latency_of_entries_ls(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                                   filtering_entries: Callable,
                                   aggregation_lvl) -> List[int]:
    entries = selector_network_entries(it_unit, aggregation_lvl)
    return [entry.timings.wait for entry in entries]


def selector_number_of_errors(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                              filtering_entries: Callable,
                              aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        entries = selector_network_entries(it_unit, aggregation_lvl)
        return [sum(1 for entry in filtering_entries(entries) if 400 <= entry.response.status < 600)]
    elif aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        return [it_unit.get_representative_trace_view().get_number_network_errors()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


def selector_payload_size_of_requests(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                                      filtering_entries: Callable,
                                      aggregation_lvl) -> List[int]:
    entries = selector_network_entries(it_unit, aggregation_lvl)
    return [entry.request.bodySize
            for entry in entries
            if entry.request.bodySize >= 0]


def selector_payload_size_of_responses(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                                       filtering_entries: Callable,
                                       aggregation_lvl) -> List[int]:
    entries = selector_network_entries(it_unit, aggregation_lvl)
    data = [entry.response.bodySize for entry in entries if entry.response.bodySize >= 0]
    return data


class NetworkRequestsNumberUCE(MultiNumberUCEComparison):
    description = "Number of requests"
    name = "Quantity of Network Requests"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=NetworkRequestsNumberUCE.aggregation_lvls,
                         data_select_op=selector_number_of_entries,
                         outlier_method=outlier_method,
                         plot_config=NetworkRequestsNumberUCE.plot_config)


class NetworkRequestsNumberApp(MultiNumberUCEComparison):
    description = "Number of requests"
    name = "Quantity of Network Requests"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=NetworkRequestsNumberApp.aggregation_lvls,
                         data_select_op=selector_number_of_entries,
                         outlier_method=outlier_method,
                         plot_config=NetworkRequestsNumberApp.plot_config)


class NetworkLatencyUCE(MultiNumberUCEComparison):
    description = "Network latency of requests in milliseconds"
    name = "Latency of Network Requests"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log",
                                    boxpoints='outliers')
    use_case_whitelist = [
            "Login_with_email",
            "Login_with_username",
            "Interact_with_map",
            "Book_hotel_core",
            "Search_for_bill_gates",
            "Show_cocktail_recipe_1",
            "Show_cocktail_recipe_2",
        ]

    def __init__(self, model, outlier_method=IQROutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_latency_of_entries_ls,
                         aggregation_lvls=NetworkLatencyUCE.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkLatencyUCE.plot_config,
                         use_case_whitelist=NetworkLatencyUCE.use_case_whitelist)


class NetworkLatencyApp(MultiNumberUCEComparison):
    description = "Network latency of requests in milliseconds"
    name = "Latency of Network Requests"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log")

    def __init__(self, model, outlier_method=IQROutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_latency_of_entries_ls,
                         aggregation_lvls=NetworkLatencyApp.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkLatencyApp.plot_config)


class NetworkNumberErrors(MultiNumberUCEComparison):
    description = "Number of network errors"
    name = "Quantity of Network Errors"
    aggregation_lvls = [AggregationLevel.APP, AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_number_of_errors,
                         aggregation_lvls=NetworkNumberErrors.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkNumberErrors.plot_config)


class NetworkPayloadSizeRequestUCE(MultiNumberUCEComparison):
    description = "Payload size of network requests"
    name = "Payload Size of Network Requests"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log")
    use_case_whitelist = [
        "Login_with_email",
        "Interact_with_map",
        "Book_hotel_core",
        "Search_for_bill_gates",
        "Show_cocktail_recipe_1",
        "Show_cocktail_recipe_2",
    ]

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_payload_size_of_requests,
                         aggregation_lvls=NetworkPayloadSizeRequestUCE.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkPayloadSizeRequestUCE.plot_config,
                         use_case_whitelist=NetworkPayloadSizeRequestUCE.use_case_whitelist)


class NetworkPayloadSizeRequestApp(MultiNumberUCEComparison):
    description = "Payload size of network requests"
    name = "Payload Size of Network Requests"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log")

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_payload_size_of_requests,
                         aggregation_lvls=NetworkPayloadSizeRequestApp.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkPayloadSizeRequestApp.plot_config)


class NetworkPayloadSizeResponseUCE(MultiNumberUCEComparison):
    description = "Payload size of network responses"
    name = "Payload Size of Network Responses"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log")
    use_case_whitelist = [
        "Book_hotel_core",
        "Interact_with_map",
        "Login_with_email",
        "Search_for_bill_gates",
        "Show_cocktail_recipe_1",  # Rejected
    ]

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_payload_size_of_responses,
                         aggregation_lvls=NetworkPayloadSizeResponseUCE.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkPayloadSizeResponseUCE.plot_config,
                         use_case_whitelist=NetworkPayloadSizeResponseUCE.use_case_whitelist)


class NetworkPayloadSizeResponseApp(MultiNumberUCEComparison):
    description = "Payload size of network responses"
    name = "Payload Size of Network Responses"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    # axis_type="linear",
                                    axis_type="log")

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_payload_size_of_responses,
                         aggregation_lvls=NetworkPayloadSizeResponseApp.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=NetworkPayloadSizeResponseApp.plot_config)
