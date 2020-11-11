# -*- coding: utf-8 -*-
import traceback

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER
from datasets import matrics_datasets
from outlierdetection.univariateoutlierdetection import OUTLIER_NAME_INSTANCE_MAP, UNIVARIATE_OUTLIER_DETECTORS
from util import configutil
from util.configutil import IMG_PATH_PREFIX, IMAGE_DIR, MATRICS_CFG_APP_FILTER_LIST
from apps import metricsapp, visualizationapp, usecasestatisticsapp, correlationanalysisapp, \
    generalapp, distributionanalysisapp
from matrics import Matrics


DROPDOWN_SELECTION_DATASETS = "selection-datasets"
LOADING_START_ANALYSIS = "loading-start-analysis"
BUTTON_START_ANALYSIS = "btn-start-analysis"
BUTTON_ICON = html.I(className="fa fa-chart-bar", style={'padding-right': '5px'})
TAB_0_LEVEL_CONTENT_CONTAINER = "tab-0-level-content-container"

app.layout = dbc.Container(id="index", children=[
    # Header
    dbc.Navbar([
        dbc.Col(
            dbc.NavbarBrand("Matrics: Usability Analysis of Android Applications",
                            href="#",
                            style={'font-size': '2rem'}),
            sm=3,
            md=11),
        dbc.Col(
            html.Img(src=f'{IMG_PATH_PREFIX}/{IMAGE_DIR}/dash-logo-by-plotly-stripe-inverted.png',
                     height="40px",
                     width="auto")
        ),
    ],
        color="black",
        dark=True,
    ),

    dbc.Container(id="upper-tab-container", className="upper-tab-container", children=[
        dbc.Row([
            # Configuration
            dbc.Col(id="configuration-col", className="col-lg-3 upper-col", children=[
                html.H3('Configuration'),
                dbc.Label('togape_config_file: ToGAPE configuration file'),
                dbc.Input(id='config-togape-config-file',
                          # value=configutil.TOGAPE_CONFIG_FILE_RECIPE,
                          # value=configutil.TOGAPE_CONFIG_FILE_DATING,
                          # value=configutil.TOGAPE_CONFIG_FILE_TRAVEL,
                          # value=configutil.TOGAPE_CONFIG_FILE_SOCIAL,
                          # value=configutil.TOGAPE_CONFIG_FILE_SOCIAL_2,
                          # value=configutil.TOGAPE_CONFIG_FILE_DATING_2,
                          # value=configutil.TOGAPE_CONFIG_FILE_RECIPE_2,
                          # value=configutil.TOGAPE_CONFIG_FILE_TRAVEL_2,
                          value=configutil.TOGAPE_CONFIG_FILE_ALL,
                          type='text',
                          style={
                              'margin-bottom': '.5rem',
                              'padding-left': '0.5rem',
                              'padding-right': '0.5rem',
                          }
                ),
                dbc.Label('Univariate outlier method'),
                dcc.Dropdown(
                    id="selection-univariate-outlier-detection",
                    options=[{'label': uo.name, 'value': uo.name} for uo in UNIVARIATE_OUTLIER_DETECTORS],
                    value=UNIVARIATE_OUTLIER_DETECTORS[0].name,
                    multi=False,
                    style={'margin-bottom': '.5rem'}
                ),
                dbc.Label('Dataset'),
                dcc.Dropdown(
                    id=DROPDOWN_SELECTION_DATASETS,
                    options=[{'label': ds, 'value': ds} for ds in matrics_datasets],
                    value="all",
                    # value="category_travel",
                    # value="category_dating",
                    # value="category_recipe",
                    # value="category_social",
                    # value="me.tutti.tutti",
                    # value="com.reddit.frontpage",
                    # value="com.twitter.android.lite",
                    # value="com.ninegag.android.app",
                    # value="com.kuwaitairways.mapps",
                    # value="com.wego.android",
                    # value="com.hostelworld.app",
                    # value="com.ajnsnewmedia.kitchenstories",
                    # value="com.lovelyAI.CocktailsBarLiquorRecipes",
                    # value="fr.cookbook",
                    # value="com.hurrythefoodup.app",
                    # value="com.datemyage",
                    # value="category_flashlight",
                    multi=False,
                    style={'margin-bottom': '.5rem'}
                ),
                dbc.Button(children=[BUTTON_ICON, "Run Analysis"],
                           id=BUTTON_START_ANALYSIS,
                           n_clicks=0,
                           color="primary",
                           className="analysis-button",
                ),
            ]),
            # General information
            dbc.Col(id="general-col", className="col-lg-9 upper-col", children=[
                generalapp.layout
            ])
        ]),
        dbc.Row([
            dbc.Col(id="col3", children=[
                # TODO there are some cool loading animations: https://community.plot.ly/t/loading-states-api-and-a-loading-component-prerelease/16406
                # TODO create a matrix animation loading
                # trigger loading animation while analysis is running
                dcc.Loading(id=LOADING_START_ANALYSIS, children=[], type="default")
            ])
        ])
    ]),

    # Tabs
    dbc.Container(id="tabs-container", className="tabs-container-root", style={"padding-top": "15px"}, children=[
        html.H3('Results'),
        dbc.Tabs(
            id="tabs",
            # style={"height": "20", "verticalAlign": "middle"},
            children=[
                dbc.Tab(label="Visualization", tab_id="visualization_tab"),
                dbc.Tab(label="Metrics", tab_id="metrics_tab"),
                dbc.Tab(label="Use Case Statistics", tab_id="use_case_statistics_tab"),
                dbc.Tab(label="Correlation Analysis", tab_id="correlations_tab"),
                dbc.Tab(label="Distribution Analysis", tab_id="distribution_analysis_tab"),
            ],
            # active_tab="visualization_tab",
            # active_tab="metrics_tab",
            # active_tab="use_case_statistics_tab",
            active_tab="correlations_tab",
            className="tabs-root tabs-custom",
        ),
    ]),

    # Tab content
    dbc.Container(id=TAB_0_LEVEL_CONTENT_CONTAINER, className="row tab-0-level"),

    html.Link(href="/css/all.css", rel="stylesheet"),
    html.Link(href="/css/fonts/Dosis.css", rel="stylesheet"),
    html.Link(href="/css/fonts/OpenSans.css", rel="stylesheet"),
    html.Link(href="/css/fonts/Ubuntu.css", rel="stylesheet"),
    html.Link(href="/css/custom.css", rel="stylesheet"),
    html.Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", rel="stylesheet"),
    # I don't know why this doesn't work
    # html.Link(href="/css/font-awesome.min.css", rel="stylesheet"),
    dbc.Container(id=ANALYSIS_FINISHED_CONTAINER, style={'display': 'none'})
],
    className="index-container"
)


@app.callback(Output(TAB_0_LEVEL_CONTENT_CONTAINER, "children"),
              [Input("tabs", "active_tab")])
def render_content(tab):
    if tab == "visualization_tab":
        return visualizationapp.layout
    elif tab == "metrics_tab":
        return metricsapp.layout
    elif tab == "use_case_statistics_tab":
        return usecasestatisticsapp.layout
    elif tab == "correlations_tab":
        return correlationanalysisapp.layout
    elif tab == "distribution_analysis_tab":
        return distributionanalysisapp.layout
    else:
        raise NotImplementedError(f"Unknown tab: {tab}")


@app.callback(
    [Output(LOADING_START_ANALYSIS, "children"),
     Output(ANALYSIS_FINISHED_CONTAINER, 'children'),
     Output(BUTTON_START_ANALYSIS, 'children'),
     ],
    [Input(BUTTON_START_ANALYSIS, 'n_clicks')],
    [State('config-togape-config-file', 'value'),
     State('selection-univariate-outlier-detection', 'value'),
     State(DROPDOWN_SELECTION_DATASETS, 'value'),])
def start_analysis(n_clicks,
                   togape_config_file,
                   univariate_outlier_method_name,
                   dataset_name):

    analysis_finished_child = None
    button_analysis_children = [BUTTON_ICON, "Run Analysis"]
    if n_clicks > 0:
        univariate_outlier_method = OUTLIER_NAME_INSTANCE_MAP[univariate_outlier_method_name]
        dataset = matrics_datasets[dataset_name]
        matrics_config = {MATRICS_CFG_APP_FILTER_LIST: dataset}
        app.matrics_ = Matrics(togape_config_file=togape_config_file,
                               matrics_config=matrics_config,
                               univariate_outlier_method=univariate_outlier_method)
        # Start analysis
        try:
            app.matrics_.start()
            analysis_finished_child = []
            button_analysis_children = [BUTTON_ICON, "Rerun Analysis"]
        except Exception as e:
            # Notification sound
            app.matrics_.play_sound(successful=False)
            print(traceback.format_exc())
            raise e

    return None, analysis_finished_child, button_analysis_children


if __name__ == "__main__":
    app.run_server(host="0.0.0.0",
                   debug=True,
                   dev_tools_hot_reload=True)
