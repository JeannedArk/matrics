# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from apps.correlations import metricscorrelations, usecasecorrelations, playstoremetricscorrelations

CORRELATIONS_TABS_ID = "metrics-correlations-tabs-id"
CORRELATIONS_TABS_CONTENT_ID = "metrics-correlations-tabs-content-id"


layout = dbc.Container([
    dbc.Container(className="tab-1-level-tab-container", children=[
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Correlation"]),
            dbc.CardBody([
                html.P("- Positive Correlation: both variables change in the same direction.", className="card-text"),
                html.P("- Neutral Correlation: No relationship in the change of the variables.", className="card-text"),
                html.P("- Negative Correlation: variables change in opposite directions. ", className="card-text"),
                html.P("It is easy to calculate and interpret when both variables have a well understood Gaussian distribution."
                       " When we do not know the distribution of the variables, we must use nonparametric rank correlation "
                       "methods.", className="card-text"),
                html.H6("Pearson’s Correlation"),
                html.P("The Pearson correlation coefficient can be used to summarize the strength of the "
                       "linear relationship between two data samples. The use of mean and standard deviation in the calculation"
                       " suggests the need for the two data samples to have a Gaussian or Gaussian-like distribution.", className="card-text"),
                html.H6("Spearman’s Correlation"),
                html.P("Two variables may be related by a nonlinear relationship, such that the"
                       "relationship is stronger or weaker across the distribution of the variables. Further, the two variables"
                       " being considered may have a non-Gaussian distribution. In this case, the Spearman’s correlation "
                       "coefficient can be used to summarize the strength between the two data samples. This test of "
                       "relationship can also be used if there is a linear relationship between the variables, but will have "
                       "slightly less power (e.g. may result in lower coefficient scores).", className="card-text"),
                html.H6("Kendall’s Correlation"),
                html.P("Kendall's correlation coefficient is also based on variable ranks. However, unlike Spearman's "
                       "coefficient, Kendalls' τ does not take into account the difference between ranks — only directional "
                       "agreement. Therefore, this coefficient is more appropriate for discrete data.", className="card-text"),
                html.P("Copied from: machinelearningmastery.com", className="card-text"),
            ]),
        ]),
        dbc.Card([
            dbc.CardHeader(className="card-header", children=["Statistical Significance"]),
            dbc.CardBody([
                html.P("The statistical significance alpha value is set to 0.05."
                       "All values not agreeing with the significance level are not available in the heatmap.", className="card-text"),
            ]),
        ]),
        dbc.Tabs(
            id=CORRELATIONS_TABS_ID,
            # style={"height": "20", "verticalAlign": "middle"},
            children=[
                dbc.Tab(label="Metrics Correlations", tab_id="metrics_correlations_tab"),
                dbc.Tab(label="Play Store Metrics Correlations", tab_id="play_store_metrics_correlations_tab"),
                dbc.Tab(label="Use Case Correlations", tab_id="use_case_correlations_tab"),
            ],
            active_tab="metrics_correlations_tab",
            # active_tab="play_store_metrics_correlations_tab",
            # active_tab="use_case_correlations_tab",
            className="tabs-custom",
        ),
    ]),

    # Tab content
    dbc.Container(id=CORRELATIONS_TABS_CONTENT_ID, className="row tab-1-level-container-container"),
],
    className="tab_div tab-div-custom"
)


@app.callback(Output(CORRELATIONS_TABS_CONTENT_ID, "children"),
              [Input(CORRELATIONS_TABS_ID, "active_tab")])
def render_content(tab):
    if tab == "metrics_correlations_tab":
        return metricscorrelations.layout
    elif tab == "play_store_metrics_correlations_tab":
        return playstoremetricscorrelations.layout
    elif tab == "use_case_correlations_tab":
        return usecasecorrelations.layout
    else:
        raise NotImplementedError(f"Unknown tab: {tab}")
