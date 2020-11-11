# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from apps.visualization import visualizationappB, usecasevisualizationapp, apphomestatevisualizationapp


VISUALIZATION_TABS_ID = "visualization-tabs-id"
VISUALIZATION_TABS_CONTENT_ID = "visualization-tabs-content-id"

layout = dbc.Container([
    dbc.Container(className="tab-1-level-tab-container", children=[
        dbc.Tabs(
            id=VISUALIZATION_TABS_ID,
            # style={"height": "20", "verticalAlign": "middle"},
            children=[
                # dbc.Tab(label="Visualization", tab_id="visualization_tab"),
                dbc.Tab(label="Use Case Visualization", tab_id="use_case_visualization_tab"),
                dbc.Tab(label="App Home State", tab_id="app_home_state_tab"),
            ],
            # active_tab="visualization_tab",
            # active_tab="use_case_visualization_tab",
            active_tab="app_home_state_tab",
            className="tabs-custom",
        ),
    ]),

    # Tab content
    dbc.Container(id=VISUALIZATION_TABS_CONTENT_ID, className="row tab-1-level-container-container"),
],
    className="tab_div tab-div-custom"
)


@app.callback(Output(VISUALIZATION_TABS_CONTENT_ID, "children"),
              [Input(VISUALIZATION_TABS_ID, "active_tab")])
def render_content(tab):
    if tab == "app_home_state_tab":
        return apphomestatevisualizationapp.layout
    elif tab == "use_case_visualization_tab":
        return usecasevisualizationapp.layout
    elif tab == "visualization_tab":
        return visualizationappB.layout
    else:
        return NotImplementedError(f"Unknown tab: {tab}")
