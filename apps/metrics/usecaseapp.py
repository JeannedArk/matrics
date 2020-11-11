# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app

from metrics.ucecomparison import usecasemetrics
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Use Case Metrics"]),
            dbc.CardBody([
                html.P(
                    "Metrics that evaluate use cases like path length. It is not about the aggregation level 'use case'.",
                    className="card-text"),
            ]),
        ])
    ]),
    usecasemetrics.UseCaseLengthUseCaseExecutions.ui_element(),
    usecasemetrics.UseCaseComputedUseCaseExecutionsNumber.ui_element(),
    usecasemetrics.UseCaseVerifiedUseCaseExecutionsNumber.ui_element(),
    usecasemetrics.UseCaseRatioVerifiedComputedUseCaseExecutionsNumber.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(usecasemetrics.UseCaseLengthUseCaseExecutions.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def use_case_length_use_case_executions_ctr(_):
    return get_graph(usecasemetrics.UseCaseLengthUseCaseExecutions.get_id())


@app.callback(
    Output(usecasemetrics.UseCaseComputedUseCaseExecutionsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def use_case_computed_use_case_executions_number_ctr(_):
    return get_graph(usecasemetrics.UseCaseComputedUseCaseExecutionsNumber.get_id())


@app.callback(
    Output(usecasemetrics.UseCaseVerifiedUseCaseExecutionsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def use_case_verified_use_case_executions_number_ctr(_):
    return get_graph(usecasemetrics.UseCaseVerifiedUseCaseExecutionsNumber.get_id())


@app.callback(
    Output(usecasemetrics.UseCaseRatioVerifiedComputedUseCaseExecutionsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def use_case_ratio_computed_verified_use_case_executions_number_ctr(_):
    return get_graph(usecasemetrics.UseCaseRatioVerifiedComputedUseCaseExecutionsNumber.get_id())
