# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from apps.apputil import show_info, app_selection, ANALYSIS_FINISHED_CONTAINER

from metrics.ucecomparison import modelmetrics
from visualization import graphviz


SELECTION_MODEL_GRAPH_DIV = "selection-model-overall-graph-div"
SIDE_NAVIGATION_INFO_BAR_CONTAINER = "sidenav-parent"
MODEL_GRAPH_DIV = "model-overall-graph-div"
VISUALIZATION_CONTAINER = "visualization-container"

layout = dbc.Container(id=VISUALIZATION_CONTAINER, children=[
    dbc.Container(id=SIDE_NAVIGATION_INFO_BAR_CONTAINER, children=[]),

    dbc.Container(id='graph-main', children=[
        dbc.Label('Display overall execution graphs'),
        dcc.Dropdown(
            id=SELECTION_MODEL_GRAPH_DIV,
            options=[],
            value=None,
            multi=False,
            style={'margin-bottom': '.5rem'}
        ),
        dbc.Label("Note: For bigger graphs the visualization can take a while."),
        dbc.Container(id=MODEL_GRAPH_DIV, children=[]),
    ]),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(MODEL_GRAPH_DIV, 'children'),
    [Input(SELECTION_MODEL_GRAPH_DIV, 'value')]
)
def model_graph_overall_ctr(app_selectionv):
    model_html_children = []
    if hasattr(app, 'matrics_'):
        model_metrics = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        model_graphs = model_metrics.plot()
        sel = app_selectionv
        model_graph = list(model_graphs.values())[0] if sel is None else model_graphs[sel]
        model_html_children = [
            html.P("Overall execution model"),
            dbc.Container(id=f'Graph {sel}', children=model_graph, style={"border": "1px solid black"})
        ]

    return model_html_children


@app.callback(
    Output(SIDE_NAVIGATION_INFO_BAR_CONTAINER, 'children'),
    [Input(graphviz.OVERALL_GRAPH_HTML_ID, 'selection')],
    [State(SELECTION_MODEL_GRAPH_DIV, 'value')])
def model_graph_selection_info_ctr(selection, app_selectionv):
    if hasattr(app, 'matrics_') and app_selectionv is not None:
        return show_info(selection, app_selectionv)
    return None


@app.callback(
    [Output(SELECTION_MODEL_GRAPH_DIV, 'options'),
     Output(SELECTION_MODEL_GRAPH_DIV, 'value')],
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children'),
     Input(VISUALIZATION_CONTAINER, 'children')]
)
def app_selection_ctr(apps_overview, _):
    """
    Dropdown options.
    We need the input parameter VISUALIZATION_CONTAINER to enable the proper reload when refreshing the page.
    """
    return app_selection()
