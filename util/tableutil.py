# -*- coding: utf-8 -*-
import dash_html_components as html, dash_table
import pandas as pd

import colorconstants


def create_table_html(df: pd.DataFrame):
    indices = df.columns.values
    table_entries = [html.Tr([html.Th(idx) for idx in indices])]
    for index, row in df.iterrows():
        info = html.Tr([html.Td(item[1]) for item in row.items()])
        table_entries.append(info)

    return html.Table(table_entries, style={'width': '100%'})


def create_table_dash_data_table(df: pd.DataFrame):
    """
    TODO Color outlier values:
    https://dash.plot.ly/datatable/style
    """

    # https://dash.plot.ly/datatable/sizing
    # TODO seems like there is a bug, making this scrollable
    dt = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        # style_table={
        #     'maxHeight': '10',
        #     'overflowY': 'scroll',
        # },
        style_cell={
            'textAlign': 'left',
        },
        style_header={
            'backgroundColor': colorconstants.RGB_COLOR_LIGHT_GREY
        },
    )

    return dt
