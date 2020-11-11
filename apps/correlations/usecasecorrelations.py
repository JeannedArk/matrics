# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from analysis.correlations import UseCaseCorrelations
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    UseCaseCorrelations.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(UseCaseCorrelations.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def use_case_correlation_ctr(_):
    return get_graph(UseCaseCorrelations.get_id())
