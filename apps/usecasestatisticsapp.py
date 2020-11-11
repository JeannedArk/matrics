# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from analysis import usecaseanalysis
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    usecaseanalysis.UseCaseOverview.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(usecaseanalysis.UseCaseOverview.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def analysis_use_case_overview_ctr(_):
    return get_graph(usecaseanalysis.UseCaseOverview.get_id())
