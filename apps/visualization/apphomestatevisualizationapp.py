# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from apps.apputil import show_info, app_selection, ANALYSIS_FINISHED_CONTAINER

from metrics.ucecomparison import modelmetrics
from metrics.ucecomparison.modelmetrics import ModelGraphs
from util import configutil
from util.uiutil import header_metric

SIDE_NAVIGATION_INFO_BAR_CONTAINER_2 = "sidenav-parent-2"
MODEL_APP_HOME_STATE_GRAPH_DIV = "model-app-home-state-div"
SELECTION_MODEL_GRAPH_DIV_2 = "selection-model-graph-2-div"
VISUALIZATION_CONTAINER_2 = "visualization-container-2-div"


layout = dbc.Container(id=VISUALIZATION_CONTAINER_2, children=[

    dbc.Container(id=SIDE_NAVIGATION_INFO_BAR_CONTAINER_2, children=[]),

    dbc.Container(id='graph-main', children=[
        dbc.Label('Display use case graphs'),
        dcc.Dropdown(
            id=SELECTION_MODEL_GRAPH_DIV_2,
            options=[],
            value=None,
            multi=False,
            style={'margin-bottom': '.5rem'}
        ),
        dbc.Label("Note: For bigger graphs the visualization can take a while."),
        dbc.Container(id=MODEL_APP_HOME_STATE_GRAPH_DIV, children=[]),
    ]),
],
    className="tab_div tab-div-custom",
    style={"padding-top": "5px"},
)


@app.callback(
    Output(MODEL_APP_HOME_STATE_GRAPH_DIV, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV_2, 'value')]
)
def model_app_home_state_graph_ctr(app_selectionv):
    model_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics: ModelGraphs = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        model_graphs = model_metrics.get_app_home_state_graphs()
        sel = app_selectionv
        model_graph = list(model_graphs.values())[0] if sel is None else model_graphs[sel]
        model_html_children = [
            header_metric("Base graph for use case identification with tagged app home state"),
            dbc.Container(id=f'model-app-home-state-graph-{sel}-div',
                          children=model_graph,
                          style={"border": "1px solid black", "width": configutil.MATRICS_VISUALIZATION_WIDTH})
        ]

    return model_html_children


# @app.callback(
#     Output(SIDE_NAVIGATION_INFO_BAR_CONTAINER, 'children'),
#     [Input(graphviz.USE_CASE_BASE_DEFAULT_GRAPH_HTML_ID, 'selection')],
#     [State(SELECTION_MODEL_GRAPH_DIV_2, 'value')])
# def model_graph_selection_info_use_case_base_graph_ctr(selection_use_case_base, app_selectionv):
#     if hasattr(app, 'matrics_') and app_selectionv is not None:
#         return show_info(selection_use_case_base, app_selectionv)
#     return None


@app.callback(
    [Output(SELECTION_MODEL_GRAPH_DIV_2, 'options'),
     Output(SELECTION_MODEL_GRAPH_DIV_2, 'value')],
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children'),
     Input(VISUALIZATION_CONTAINER_2, 'children')]
)
def app_selection_ctr(apps_overview, _):
    """
    Dropdown options.
    We need the input parameter USE_CASE_VISUALIZATION_CONTAINER to enable the proper reload when refreshing the page.
    """
    return app_selection()
