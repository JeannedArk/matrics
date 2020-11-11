# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app

from metrics.ucecomparison import modelmetrics

ANALYSIS_FINISHED_CONTAINER = "analysis-finished"


def get_graph(metric_id):
    graph = None
    if hasattr(app, 'matrics_'):
        metric_ = app.matrics_.model.model_accessors[metric_id]
        graph = metric_.plot()

    return graph


def create_sidenav_bar(children_elements):
    width = 800
    sidenav_close = [html.A("Click on an empty spot in the graph to close this side bar.", id="sidenav-close")]
    ls = sidenav_close + children_elements
    return [
        html.Link(href="/css/sidenav.css", rel="stylesheet"),
        dbc.Container(id="sidenav-info", className="sidenav", style={'width': f'{width}px'}, children=ls),
    ]


def show_info(selection, app_selectionv):
    child_elements = []
    if selection['nodes']:
        model_metrics = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        node_info = model_metrics.node_info(app_selectionv, selection['nodes'][0])
        child_elements.extend(node_info)
    if selection['edges']:
        model_metrics = app.matrics_.model.model_accessors[modelmetrics.ModelGraphs.get_id()]
        edge_info = model_metrics.edges_info(app_selectionv, selection['edges'])
        child_elements.extend(edge_info)
    if child_elements:
        return create_sidenav_bar(child_elements)


def app_selection():
    selection_model_div_options = []
    selection_model_div_value = []
    if hasattr(app, 'matrics_') and app.matrics_ is not None:
        apps = app.matrics_.apps
        selection_model_div_options = [{'label': a.package_name, 'value': a.package_name} for a in apps]
        selection_model_div_value = apps[0].package_name

    return selection_model_div_options, selection_model_div_value
