# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output

from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER
from util import tableutil


APPS_OVERVIEW_CONTAINER = "apps-overview"

layout = dbc.Container([
    dbc.Container(id=APPS_OVERVIEW_CONTAINER,
                  className='column',
                  children=[],
                  style={'margin-right': '5px', 'margin-bottom': '10px'}),
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(APPS_OVERVIEW_CONTAINER, 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def apps_overview_ctr(_):
    table = None
    if hasattr(app, 'matrics_'):
        apps = app.matrics_.model.get_apps_sorted()
        table = create_apps_overview_table(apps)

    return table


def create_apps_overview_table(matrics_apps):
    df = pd.DataFrame(
        data={
            'Package name': [app.package_name for app in matrics_apps],
            'Version': [app.version_name for app in matrics_apps],
            'Domain': [app.domain.value for app in matrics_apps],
        }
    )

    return [tableutil.create_table_html(df)]
