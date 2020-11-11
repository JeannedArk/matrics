# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps.apputil import ANALYSIS_FINISHED_CONTAINER, get_graph
from metrics.ucecomparison import staticmetrics

layout = dbc.Container([
    staticmetrics.StaticPermissionsNumber.ui_element(),
    # staticmetrics.StaticReceiversNumber.ui_element(),
    # staticmetrics.StaticVersionNumber.ui_element(),
    staticmetrics.StaticPermissionsDistributionAmongApps.ui_element(),
    staticmetrics.StaticAppPermissionsDistributionAmongPermissions.ui_element(),
    staticmetrics.StaticAdTrackingLibraryNumber.ui_element(),
    # staticmetrics.StaticPackageSize.ui_element()
],
    className="tab_div tab-div-custom"
)


@app.callback(
    Output(staticmetrics.StaticPermissionsNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def permissions_number_ctr(_):
    return get_graph(staticmetrics.StaticPermissionsNumber.get_id())


@app.callback(
    Output(staticmetrics.StaticPermissionsDistributionAmongApps.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def permissions_distribution_among_apps_ctr(_):
    return get_graph(staticmetrics.StaticPermissionsDistributionAmongApps.get_id())


@app.callback(
    Output(staticmetrics.StaticAppPermissionsDistributionAmongPermissions.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def permissions_app_permissions_distribution_among_permissions_ctr(_):
    return get_graph(staticmetrics.StaticAppPermissionsDistributionAmongPermissions.get_id())


# @app.callback(
#     Output(staticmetrics.StaticReceiversNumber.get_ui_loading_id(), 'children'),
#     [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
# )
# def static_receivers_number_ctr(_):
#     return get_graph(staticmetrics.StaticReceiversNumber.get_id())


# @app.callback(
#     Output(staticmetrics.StaticVersionNumber.get_ui_loading_id(), 'children'),
#     [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
# )
# def static_version_number_ctr(_):
#     return get_graph(staticmetrics.StaticVersionNumber.get_id())


# @app.callback(
#     Output('loading-package-size-graph', 'children'),
#     [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
# )
# def static_package_size_ctr(_):
#     return get_graph(staticmetrics.StaticPackageSize.get_id())


@app.callback(
    Output(staticmetrics.StaticAdTrackingLibraryNumber.get_ui_loading_id(), 'children'),
    [Input(ANALYSIS_FINISHED_CONTAINER, 'children')]
)
def static_ad_tracking_library_number_ctr(_):
    return get_graph(staticmetrics.StaticAdTrackingLibraryNumber.get_id())
