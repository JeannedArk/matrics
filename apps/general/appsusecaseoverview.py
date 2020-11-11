# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from analysis import usecaseanalysis
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    usecaseanalysis.AppsUseCaseExecutionsOverview.ui_element(show_header=False),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(usecaseanalysis.AppsUseCaseExecutionsOverview.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def apps_use_case_executions_overview_ctr(_):
    return get_graph(usecaseanalysis.AppsUseCaseExecutionsOverview.get_id())
