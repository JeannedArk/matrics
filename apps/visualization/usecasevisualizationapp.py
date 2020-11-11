# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from apps.apputil import show_info, app_selection, ANALYSIS_FINISHED_CONTAINER

from metrics.ucecomparison import modelmetrics
from metrics.ucecomparison.modelmetrics import ModelGraphs
from visualization import graphviz
from util.uiutil import header_metric


SIDE_NAVIGATION_INFO_BAR_CONTAINER = "sidenav-use-case-parent"
SIDE_NAVIGATION_INFO_BAR_USE_CASE_EXECUTION_CONTAINER = "sidenav-use-case-exec-parent"
SELECTION_MODEL_GRAPH_DIV = "selection-model-graph-div"
MODEL_USE_CASE_BASE_GRAPH_DIV = "model-use-case-base-graph-custom-div"
MODEL_USE_CASE_BASE_UNMODIFIED_GRAPH_DIV = "model-use-case-base-unmodified-graph-custom-div"
MODEL_USE_CASE_BASE_TRANSFORMED_GRAPH_DIV = "model-use-case-base-transformed-graph-custom-div"
MODEL_USE_CASE_EXECUTIONS_CONTAINER = "model-use-case-executions"
USE_CASE_VISUALIZATION_CONTAINER = "use-case-visualization-container"


layout = dbc.Container(id=USE_CASE_VISUALIZATION_CONTAINER, children=[

    dbc.Container(id=SIDE_NAVIGATION_INFO_BAR_CONTAINER, children=[]),

    dbc.Container(id='graph-main', children=[
        dbc.Label('Display use case graphs'),
        dcc.Dropdown(
            id=SELECTION_MODEL_GRAPH_DIV,
            options=[],
            value=None,
            multi=False,
            style={'margin-bottom': '.5rem'}
        ),
        dbc.Label("Note: For bigger graphs the visualization can take a while."),
        dbc.Container(id=MODEL_USE_CASE_BASE_GRAPH_DIV, children=[]),
        # dbc.Container(id=MODEL_USE_CASE_BASE_UNMODIFIED_GRAPH_DIV, children=[]),
        # dbc.Container(id=MODEL_USE_CASE_BASE_TRANSFORMED_GRAPH_DIV, children=[]),
        dbc.Container(id=MODEL_USE_CASE_EXECUTIONS_CONTAINER, children=[]),
    ]),
],
    className="tab_div tab-div-custom",
    style={"padding-top": "5px"},
)


@app.callback(
    Output(MODEL_USE_CASE_BASE_GRAPH_DIV, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV, 'value')]
)
def model_use_case_base_graph_ctr(app_selectionv):
    model_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics: ModelGraphs = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        model_graphs = model_metrics.get_use_case_base_graphs()
        sel = app_selectionv
        model_graph = list(model_graphs.values())[0] if sel is None else model_graphs[sel]
        model_html_children = [
            header_metric("Base graph for use case identification"),
            dbc.Container(id=f'Base use case graph {sel}', children=model_graph, style={"border": "1px solid black"})
        ]

    return model_html_children


@app.callback(
    Output(MODEL_USE_CASE_BASE_TRANSFORMED_GRAPH_DIV, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV, 'value')]
)
def model_use_case_base_transformed_graph_ctr(app_selectionv):
    model_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics: ModelGraphs = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        model_graphs = model_metrics.plot_use_case_base_transformed_graph()
        sel = app_selectionv
        model_graph = list(model_graphs.values())[0] if sel is None else model_graphs[sel]
        model_html_children = [
            html.P("Base transformed graph for use case identification"),
            dbc.Container(id=f'Base use case transformed graph {sel}', children=model_graph, style={"border": "1px solid black"})
        ]

    return model_html_children


@app.callback(
    Output(MODEL_USE_CASE_BASE_UNMODIFIED_GRAPH_DIV, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV, 'value')]
)
def model_use_case_base_unmodified_graph_ctr(app_selectionv):
    model_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics: ModelGraphs = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        model_graphs = model_metrics.plot_use_case_base_unmodified_graph()
        sel = app_selectionv
        model_graph = list(model_graphs.values())[0] if sel is None else model_graphs[sel]
        model_html_children = [
            header_metric("Base unmodified graph for use case identification"),
            dbc.Container(id=f'Base use case transformed graph {sel}', children=model_graph, style={"border": "1px solid black"})
        ]

    return model_html_children


@app.callback(
    Output(MODEL_USE_CASE_EXECUTIONS_CONTAINER, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV, 'value')]
)
def use_case_execution_graphs_ctr(app_selectionv):
    use_case_execution_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics: ModelGraphs = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        sel = app_selectionv
        use_case_executions_graphs = model_metrics.plot_use_case_executions()
        use_case_execution_html_children = list(use_case_executions_graphs.values())[0] if sel is None else use_case_executions_graphs[sel]
    return use_case_execution_html_children


# PRECOMPUTED_USE_CASE_EXECUTION_HTML_IDS = [f"network_{i}_container" for i in range(20)]
# ls = [Input(graphviz.USE_CASE_BASE_GRAPH_HTML_ID, 'selection')] + [Input(html_id, 'selection') for html_id in PRECOMPUTED_USE_CASE_EXECUTION_HTML_IDS]
@app.callback(
    Output(SIDE_NAVIGATION_INFO_BAR_CONTAINER, 'children'),
    [Input(graphviz.USE_CASE_BASE_DEFAULT_GRAPH_HTML_ID, 'selection')],
    [State(SELECTION_MODEL_GRAPH_DIV, 'value')])
def model_graph_selection_info_use_case_base_graph_ctr(selection_use_case_base, app_selectionv):
    if hasattr(app, 'matrics_') and app_selectionv is not None:
        return show_info(selection_use_case_base, app_selectionv)
    return None


@app.callback(
    [Output(SELECTION_MODEL_GRAPH_DIV, 'options'),
     Output(SELECTION_MODEL_GRAPH_DIV, 'value')],
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children'),
     Input(USE_CASE_VISUALIZATION_CONTAINER, 'children')]
)
def app_selection_ctr(apps_overview, _):
    """
    Dropdown options.
    We need the input parameter USE_CASE_VISUALIZATION_CONTAINER to enable the proper reload when refreshing the page.
    """
    return app_selection()
