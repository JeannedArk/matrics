# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from metrics.ucecomparison import networkmetrics
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["BrowserMob"]),
            dbc.CardBody([
                html.P("The network data is acquired by the help of a BrowserMob proxy. "
                       "For each new interaction a new BrowserMob page is created. "
                       "The data is dumped into a HAR file after the app exploration. "
                       "Follow the Readme in order to properly setup your device. ", className="card-text"),
            ]),
        ])
    ]),
    networkmetrics.NetworkRequestsNumberUCE.ui_element(),
    networkmetrics.NetworkRequestsNumberApp.ui_element(),
    networkmetrics.NetworkLatencyUCE.ui_element(),
    networkmetrics.NetworkLatencyApp.ui_element(),
    networkmetrics.NetworkNumberErrors.ui_element(),
    networkmetrics.NetworkPayloadSizeRequestUCE.ui_element(),
    networkmetrics.NetworkPayloadSizeRequestApp.ui_element(),
    networkmetrics.NetworkPayloadSizeResponseUCE.ui_element(),
    networkmetrics.NetworkPayloadSizeResponseApp.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(networkmetrics.NetworkRequestsNumberUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_requests_number_uce_ctr(_):
    return get_graph(networkmetrics.NetworkRequestsNumberUCE.get_id())


@app.callback(
    Output(networkmetrics.NetworkRequestsNumberApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_requests_number_app_ctr(_):
    return get_graph(networkmetrics.NetworkRequestsNumberApp.get_id())


@app.callback(
    Output(networkmetrics.NetworkLatencyUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_latency_uce_ctr(_):
    return get_graph(networkmetrics.NetworkLatencyUCE.get_id())


@app.callback(
    Output(networkmetrics.NetworkLatencyApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_latency_app_ctr(_):
    return get_graph(networkmetrics.NetworkLatencyApp.get_id())


@app.callback(
    Output(networkmetrics.NetworkNumberErrors.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_number_errors_ctr(_):
    return get_graph(networkmetrics.NetworkNumberErrors.get_id())


@app.callback(
    Output(networkmetrics.NetworkPayloadSizeRequestUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_payload_size_request_uce_ctr(_):
    return get_graph(networkmetrics.NetworkPayloadSizeRequestUCE.get_id())


@app.callback(
    Output(networkmetrics.NetworkPayloadSizeRequestApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_payload_size_request_app_ctr(_):
    return get_graph(networkmetrics.NetworkPayloadSizeRequestApp.get_id())


@app.callback(
    Output(networkmetrics.NetworkPayloadSizeResponseUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_payload_size_response_uce_ctr(_):
    return get_graph(networkmetrics.NetworkPayloadSizeResponseUCE.get_id())


@app.callback(
    Output(networkmetrics.NetworkPayloadSizeResponseApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def network_payload_size_response_app_ctr(_):
    return get_graph(networkmetrics.NetworkPayloadSizeResponseApp.get_id())
