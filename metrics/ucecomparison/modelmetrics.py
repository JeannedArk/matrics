# -*- coding: utf-8 -*-
import pickle
from typing import Callable, List

from aggregationlevel import AggregationLevel
from metrics.metric import *
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.dummyexplorationmodel import DummyExplorationModel
from model.explorationmodel import ExplorationModel
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector


class ModelGraphs(BaseMetric):
    description = "Overall execution graph"

    def __init__(self, model, outlier_method=None):
        self.model = model
        data = self.load_data(model)
        super().__init__("Overall execution graph",
                         model,
                         AggregationLevel.APP.iter_instance(model),
                         outlier_method,
                         data)

        self.name_data_map = {self.app_names[i]: self.data[i] for i in range(len(self.app_names))}

    def store_data(self, data, file):
        dummy_data = [DummyExplorationModel.create_from_exploration_model(app.exploration_model)
                      for app in self.model.apps]
        with open(file, 'wb') as f:
            pickle.dump(dummy_data, f)

    def compute_data(self, model):
        return [app.exploration_model for app in model.apps]

    def node_info(self, selection, node):
        return self.name_data_map[selection].node_info(node)

    def edges_info(self, selection, edges):
        return self.name_data_map[selection].edges_info(edges)

    def plot_use_case_executions(self):
        return {app_name: self.name_data_map[app_name].plot_use_case_executions() for app_name in self.name_data_map.keys()}

    def get_use_case_base_graphs(self):
        return {app_name: self.name_data_map[app_name].plot_use_case_base_graph() for app_name in self.name_data_map.keys()}

    def plot_use_case_base_unmodified_graph(self):
        return {app_name: self.name_data_map[app_name].plot_use_case_base_unmodified_graph() for app_name in self.name_data_map.keys()}

    def plot_use_case_base_transformed_graph(self):
        return {app_name: self.name_data_map[app_name].plot_use_case_base_transformed_graph() for app_name in self.name_data_map.keys()}

    def get_app_home_state_graphs(self):
        return {app_name: self.name_data_map[app_name].plot_app_home_state_graph() for app_name in self.name_data_map.keys()}

    def plot(self):
        return {app_name: self.name_data_map[app_name].plot() for app_name in self.name_data_map.keys()}


def selector_number_of_nodes(it_unit: ExplorationModel,
                             filtering_entries: Callable,
                             aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.num_nodes()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelNodesNumber(MultiNumberUCEComparison):
    description = "Number of nodes"
    name = "Quantity of Nodes"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelNodesNumber.aggregation_lvls,
                         data_select_op=selector_number_of_nodes,
                         outlier_method=outlier_method,
                         plot_config=ModelNodesNumber.plot_config)


def selector_number_of_edges(it_unit: ExplorationModel,
                             filtering_entries: Callable,
                             aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        return [len(set([f"{trans.source_state} {trans.resulting_state}" for trans in it_unit.use_case_base_graph.transitions]))]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelEdgesNumber(MultiNumberUCEComparison):
    description = "Number of distinct edges (distinct defined as source state -> resulting state)"
    name = "Quantity of Edges"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelEdgesNumber.aggregation_lvls,
                         data_select_op=selector_number_of_edges,
                         outlier_method=outlier_method,
                         plot_config=ModelEdgesNumber.plot_config)


def selector_indegree(it_unit: ExplorationModel,
                      filtering_entries: Callable,
                      aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.indegree_graph()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelIndegree(MultiNumberUCEComparison):
    description = "Avg indegree"
    name = "Indegree"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelIndegree.aggregation_lvls,
                         data_select_op=selector_indegree,
                         outlier_method=outlier_method,
                         plot_config=ModelIndegree.plot_config)


def selector_outdegree(it_unit: ExplorationModel,
                       filtering_entries: Callable,
                       aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.outdegree_graph()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelOutdegree(MultiNumberUCEComparison):
    description = "Avg outdegree"
    name = "Outdegree"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelOutdegree.aggregation_lvls,
                         data_select_op=selector_outdegree,
                         outlier_method=outlier_method,
                         plot_config=ModelOutdegree.plot_config)


def selector_node_connectivity(it_unit: ExplorationModel,
                               filtering_entries: Callable,
                               aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.k_vertex_connectivity()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelNodeConnectivity(MultiNumberUCEComparison):
    description = "Node connectivity"
    name = "Node Connectivity"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelNodeConnectivity.aggregation_lvls,
                         data_select_op=selector_node_connectivity,
                         outlier_method=outlier_method,
                         plot_config=ModelNodeConnectivity.plot_config)


def selector_edge_connectivity(it_unit: ExplorationModel,
                               filtering_entries: Callable,
                               aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.k_edge_connectivity()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelEdgeConnectivity(MultiNumberUCEComparison):
    description = "Edge connectivity"
    name = "Edge Connectivity"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelEdgeConnectivity.aggregation_lvls,
                         data_select_op=selector_edge_connectivity,
                         outlier_method=outlier_method,
                         plot_config=ModelEdgeConnectivity.plot_config)


def selector_avg_graph_depth(it_unit: ExplorationModel,
                             filtering_entries: Callable,
                             aggregation_lvl) -> List:
    if aggregation_lvl == AggregationLevel.APP:
        return [np.mean(it_unit.use_case_base_graph.graph_depth_from_home_state())]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelAvgGraphDepth(MultiNumberUCEComparison):
    description = "Avg graph depth (from home state)"
    name = "Depth from Home Screen"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelAvgGraphDepth.aggregation_lvls,
                         data_select_op=selector_avg_graph_depth,
                         outlier_method=outlier_method,
                         plot_config=ModelAvgGraphDepth.plot_config)


def selector_max_graph_depth(it_unit: ExplorationModel,
                             filtering_entries: Callable,
                             aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [max(it_unit.use_case_base_graph.graph_depth_from_home_state())]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelMaxGraphDepth(MultiNumberUCEComparison):
    description = "Max graph depth (from home state)"
    name = "Depth from Home Screen"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelMaxGraphDepth.aggregation_lvls,
                         data_select_op=selector_max_graph_depth,
                         outlier_method=outlier_method,
                         plot_config=ModelMaxGraphDepth.plot_config)


def selector_avg_shortest_path_length(it_unit: ExplorationModel,
                                      filtering_entries: Callable,
                                      aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.average_shortest_path_length()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelAvgShortestPathLength(MultiNumberUCEComparison):
    description = "Avg shortest path length"
    name = "Shortest path"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelAvgShortestPathLength.aggregation_lvls,
                         data_select_op=selector_avg_shortest_path_length,
                         outlier_method=outlier_method,
                         plot_config=ModelAvgShortestPathLength.plot_config)


def selector_density(it_unit: ExplorationModel,
                     filtering_entries: Callable,
                     aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.density()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelDensity(MultiNumberUCEComparison):
    description = "Density"
    name = "Density"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelDensity.aggregation_lvls,
                         data_select_op=selector_density,
                         outlier_method=outlier_method,
                         plot_config=ModelDensity.plot_config)


def selector_diameter(it_unit: ExplorationModel,
                      filtering_entries: Callable,
                      aggregation_lvl) -> List[float]:
    if aggregation_lvl == AggregationLevel.APP:
        return [it_unit.use_case_base_graph.diameter()]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class ModelDiameter(MultiNumberUCEComparison):
    """
    Not used
    networkx.exception.NetworkXError: Found infinite path length because the digraph is not strongly connected
    """
    description = "Diameter"
    name = "Diameter"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self, model=None, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=ModelDiameter.aggregation_lvls,
                         data_select_op=selector_diameter,
                         outlier_method=outlier_method,
                         plot_config=ModelDiameter.plot_config)
