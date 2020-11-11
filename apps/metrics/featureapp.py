# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from metrics.ucecomparison import featuremetrics
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
        ])
    ]),
    featuremetrics.FeatureNumber.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(featuremetrics.FeatureNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def feature_number_ctr(_):
    return get_graph(featuremetrics.FeatureNumber.get_id())
