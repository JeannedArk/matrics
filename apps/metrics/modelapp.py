# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph

from metrics.ucecomparison import modelmetrics


layout = dbc.Container([
    modelmetrics.ModelNodesNumber.ui_element(),
    modelmetrics.ModelEdgesNumber.ui_element(),
    # modelmetrics.ModelIndegree.ui_element(),
    # modelmetrics.ModelOutdegree.ui_element(),
    modelmetrics.ModelNodeConnectivity.ui_element(),
    modelmetrics.ModelEdgeConnectivity.ui_element(),
    modelmetrics.ModelAvgGraphDepth.ui_element(),
    # modelmetrics.ModelMaxGraphDepth.ui_element(),
    modelmetrics.ModelDensity.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(modelmetrics.ModelNodesNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_nodes_number_ctr(_):
    return get_graph(modelmetrics.ModelNodesNumber.get_id())


@app.callback(
    Output(modelmetrics.ModelEdgesNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_edges_number_ctr(_):
    return get_graph(modelmetrics.ModelEdgesNumber.get_id())


@app.callback(
    Output(modelmetrics.ModelIndegree.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_indegree_ctr(_):
    return get_graph(modelmetrics.ModelIndegree.get_id())


@app.callback(
    Output(modelmetrics.ModelOutdegree.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_outdegree_ctr(_):
    return get_graph(modelmetrics.ModelOutdegree.get_id())


@app.callback(
    Output(modelmetrics.ModelNodeConnectivity.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_node_connectivity_ctr(_):
    return get_graph(modelmetrics.ModelNodeConnectivity.get_id())


@app.callback(
    Output(modelmetrics.ModelEdgeConnectivity.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_edge_connectivity_ctr(_):
    return get_graph(modelmetrics.ModelEdgeConnectivity.get_id())


@app.callback(
    Output(modelmetrics.ModelAvgGraphDepth.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_avg_graph_depth_ctr(_):
    return get_graph(modelmetrics.ModelAvgGraphDepth.get_id())


# @app.callback(
#     Output(modelmetrics.ModelMaxGraphDepth.get_ui_loading_id(), 'children'),
#     [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
# )
# def model_max_graph_depth_ctr(_):
#     return get_graph(modelmetrics.ModelMaxGraphDepth.get_id())


@app.callback(
    Output(modelmetrics.ModelAvgShortestPathLength.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_avg_shortest_path_length_ctr(_):
    return get_graph(modelmetrics.ModelAvgShortestPathLength.get_id())


@app.callback(
    Output(modelmetrics.ModelDensity.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def model_density_ctr(_):
    return get_graph(modelmetrics.ModelDensity.get_id())

