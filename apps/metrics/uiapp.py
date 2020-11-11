# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from metrics.ucecomparison import uimetrics
from metrics.appcomparison import uimetrics as uuimetrics
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph


layout = dbc.Container([
    dbc.Container(className="cards-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Widgets"]),
            html.P("The UI analysis is based on the recognition of DM2's widgets. "
                   "Only unique widgets are considered by using the widget id.", className="card-text"),
        ])
    ]),
    uimetrics.UIInteractableVisibleWidgetsNumber.ui_element(),
    uuimetrics.UIInteractableVisibleWidgetsNumber.ui_element(),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(uimetrics.UIInteractableVisibleWidgetsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def ui_interactable_visible_widgets_number_ctr(_):
    return get_graph(uimetrics.UIInteractableVisibleWidgetsNumber.get_id())


@app.callback(
    Output(uuimetrics.UIInteractableVisibleWidgetsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def ui_interactable_visible_widgets_number_w_state_ctr(_):
    return get_graph(uuimetrics.UIInteractableVisibleWidgetsNumber.get_id())