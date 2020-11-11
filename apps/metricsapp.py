# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps.metrics import networkapp, buttonapp, uiapp, featureapp, usecaseapp, staticpropertiesapp, \
    undesiredbehaviorapp, modelapp, playstoreapp

METRICS_TABS_ID = "metrics-tabs-id"
METRICS_TABS_CONTENT_ID = "metrics-tabs-content-id"


layout = dbc.Container([
    dbc.Container(className="tab-1-level-tab-container", children=[
        dbc.Tabs(
            id=METRICS_TABS_ID,
            # style={"height": "20", "verticalAlign": "middle"},
            children=[
                dbc.Tab(label="Static Properties", tab_id="static_properties_tab"),
                dbc.Tab(label="Model", tab_id="model_tab"),
                dbc.Tab(label="Undesired Behavior", tab_id="undesired_behavior_tab"),
                dbc.Tab(label="Network", tab_id="network_tab"),
                dbc.Tab(label="Button", tab_id="button_tab"),
                dbc.Tab(label="UI", tab_id="ui_tab"),
                dbc.Tab(label="Feature", tab_id="feature_tab"),
                dbc.Tab(label="Use Case", tab_id="use_case_tab"),
                dbc.Tab(label="Play Store", tab_id="play_store_tab"),
            ],
            # active_tab="model_tab",
            active_tab="network_tab",
            # active_tab="button_tab",
            # active_tab="ui_tab",
            # active_tab="feature_tab",
            # active_tab="static_properties_tab",
            # active_tab="undesired_behavior_tab",
            # active_tab="use_case_tab",
            # active_tab="play_store_tab",
            className="tabs-custom",
        ),
    ]),

    # Tab content
    dbc.Container(id=METRICS_TABS_CONTENT_ID, className="row tab-1-level-container-container"),
],
    className="tab_div tab-div-custom"
)


@app.callback(Output(METRICS_TABS_CONTENT_ID, "children"),
              [Input(METRICS_TABS_ID, "active_tab")])
def render_content(tab):
    if tab == "model_tab":
        return modelapp.layout
    elif tab == "network_tab":
        return networkapp.layout
    elif tab == "button_tab":
        return buttonapp.layout
    elif tab == "ui_tab":
        return uiapp.layout
    elif tab == "feature_tab":
        return featureapp.layout
    elif tab == "static_properties_tab":
        return staticpropertiesapp.layout
    elif tab == "undesired_behavior_tab":
        return undesiredbehaviorapp.layout
    elif tab == "use_case_tab":
        return usecaseapp.layout
    elif tab == "play_store_tab":
        return playstoreapp.layout
    else:
        return NotImplementedError(f"Unknown tab: {tab}")
