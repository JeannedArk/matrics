# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
from apps.general import apps, appsusecaseoverview, usecaseexecutionsappsoverview


GENERAL_TABS_ID = "general-tabs-id"
GENERAL_TABS_CONTENT_ID = "general-tabs-content-id"

layout = dbc.Container([
    html.H3(style={"padding-left": "15px"}, children=["General Information"]),

    dbc.Container(style={}, children=[
        dbc.Tabs(
            id=GENERAL_TABS_ID,
            # style={"height": "20", "verticalAlign": "middle"},
            children=[
                dbc.Tab(label="Apps", tab_id="apps_tab"),
                dbc.Tab(label="Use Cases", tab_id="use_cases_tab"),
                dbc.Tab(label="UCEs", tab_id="uces_tab"),
            ],
            active_tab="apps_tab",
            # active_tab="use_cases_tab",
            className="tabs-root tabs-custom",
        ),
    ]),

    # Tab content
    dbc.Container(id=GENERAL_TABS_CONTENT_ID, className="row tab-0-level general-tab-content-container"),
],
    className="tab_div tab-div-custom"
)


@app.callback(Output(GENERAL_TABS_CONTENT_ID, "children"),
              [Input(GENERAL_TABS_ID, "active_tab")])
def render_content(tab):
    if tab == "apps_tab":
        return apps.layout
    elif tab == "use_cases_tab":
        return appsusecaseoverview.layout
    elif tab == "uces_tab":
        return usecaseexecutionsappsoverview.layout
    else:
        raise NotImplementedError(f"Unknown tab: {tab}")
