# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from metrics.ucecomparison import buttonmetrics
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Buttons"]),
            dbc.CardBody([
                html.P("UI elements are considered as button if the UI class contains 'Button' or 'Btn'. "
                       "Furthermore, we require the widget to be interactable and visible.", className="card-text"),
            ]),
        ])
    ]),
    buttonmetrics.ButtonButtonsNumberUCE.ui_element(),
    buttonmetrics.ButtonButtonsNumberApp.ui_element(),
    buttonmetrics.ButtonAreaUCE.ui_element(),
    buttonmetrics.ButtonAreaApp.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(buttonmetrics.ButtonButtonsNumberUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def button_buttons_number_ctr(_):
    return get_graph(buttonmetrics.ButtonButtonsNumberUCE.get_id())


@app.callback(
    Output(buttonmetrics.ButtonButtonsNumberApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def button_buttons_number_app_ctr(_):
    return get_graph(buttonmetrics.ButtonButtonsNumberApp.get_id())


@app.callback(
    Output(buttonmetrics.ButtonAreaUCE.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def button_area_ctr(_):
    return get_graph(buttonmetrics.ButtonAreaUCE.get_id())


@app.callback(
    Output(buttonmetrics.ButtonAreaApp.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def button_area_App_ctr(_):
    return get_graph(buttonmetrics.ButtonAreaApp.get_id())
