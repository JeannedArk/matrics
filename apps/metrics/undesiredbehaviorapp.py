# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph

from metrics.ucecomparison import undesiredbehaviormetrics

layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Unsuccessful Actions"]),
            dbc.CardBody([
                html.P("Not successful actions are transitions that are labeled as not successful by DM2.", className="card-text"),
            ]),
        ])
    ]),
    undesiredbehaviormetrics.UndesiredBehaviorCrashNumber.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(undesiredbehaviormetrics.UndesiredBehaviorCrashNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def undesired_behavior_crash_number_ctr(_):
    return get_graph(undesiredbehaviormetrics.UndesiredBehaviorCrashNumber.get_id())
