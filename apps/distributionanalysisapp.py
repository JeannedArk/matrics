# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from analysis.distribution import Distribution
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph

import analysis


layout = dbc.Container([
    Distribution.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(Distribution.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def analysis_distribution_ctr(_):
    return get_graph(Distribution.get_id())
