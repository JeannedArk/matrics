# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph

from analysis.playstorecorrelations import PlayStoreCorrelationsMetricAppAL


layout = dbc.Container([
    dbc.Container([
        PlayStoreCorrelationsMetricAppAL.ui_element(),
    ]),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(PlayStoreCorrelationsMetricAppAL.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def correlations_metric_app_level_ctr(_):
    return get_graph(PlayStoreCorrelationsMetricAppAL.get_id())
