# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph
from metrics.ucecomparison import playstoremetrics


layout = dbc.Container([
    playstoremetrics.PlayStoreRating.ui_element(),
    playstoremetrics.PlayStoreReviewNumber.ui_element(),
    playstoremetrics.PlayStoreInstallationNumber.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(playstoremetrics.PlayStoreRating.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def play_store_rating_ctr(_):
    return get_graph(playstoremetrics.PlayStoreRating.get_id())


@app.callback(
    Output(playstoremetrics.PlayStoreReviewNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def play_store_review_number_ctr(_):
    return get_graph(playstoremetrics.PlayStoreReviewNumber.get_id())


@app.callback(
    Output(playstoremetrics.PlayStoreInstallationNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def play_store_review_number_ctr(_):
    return get_graph(playstoremetrics.PlayStoreInstallationNumber.get_id())
