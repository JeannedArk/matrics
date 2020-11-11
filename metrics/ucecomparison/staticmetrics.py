# -*- coding: utf-8 -*-
import collections
from typing import Union, Callable, List

import plotly.graph_objs as go

from aggregationlevel import AggregationLevel
from metrics.metric import *


from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel

PD_FRAME_NAME = "frame"


class StaticPermissionsDistributionAmongApps(BaseMetric):
    description = "Distribution of permissions among apps"
    name = "Distribution of permissions among apps"

    def __init__(self, model, outlier_method=None, filter_non_android_perms=True):
        self.abs_distr = collections.Counter()
        self.all_permission = set()
        data = self.load_data(model, filter_non_android_perms)
        self.permission_distr_app = [(self.abs_distr[p] / len(data)) for p in self.abs_distr]
        self.permissions_name = [p for p in self.abs_distr]
        super().__init__(StaticPermissionsDistributionAmongApps.name,
                         model,
                         AggregationLevel.APP.iter_instance(model),
                         None,
                         data)

    def compute_data(self, model, filter_non_android_perms):
        data = []
        for app in model.apps:
            permissions = app.permissions
            if filter_non_android_perms:
                permissions = [p for p in permissions if p.startswith("android.permission.")]
            data.append(permissions)
            for p in permissions:
                self.all_permission.add(p)
                self.abs_distr[p] += 1
        return data

    def plot(self):
        df = pd.DataFrame({PD_FRAME_NAME: self.permission_distr_app}, index=self.permissions_name)
        pd_sorted = df.sort_values(by=[PD_FRAME_NAME])
        title = f"Metric: {self.get_id()}"
        data = [go.Bar(
            x=pd_sorted[PD_FRAME_NAME],
            y=pd_sorted.index,
            name=title,
            orientation='h'
        )]
        layout = go.Layout(
            title=title,
            xaxis={
                'title': title,
                'automargin': True
            },
            yaxis={
                'automargin': True
            },
            # margin=dict(l=210, r=25, b=20, t=0, pad=4),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        distr_among_apps = dcc.Graph(id=self.get_id(),
                                     config=dict(displayModeBar=False),
                                     figure=dict(data=data, layout=layout))

        return distr_among_apps


class StaticAppPermissionsDistributionAmongPermissions(BaseMetric):
    description = "Distribution of the apps' permissions among permissions"
    name = "Distribution of the apps' permissions among permissions"

    def __init__(self, model, outlier_method=None, filter_non_android_perms=True):
        self.abs_distr = collections.Counter()
        self.all_permission = set()
        data = self.load_data(model, filter_non_android_perms)
        self.permission_distr_app = [(self.abs_distr[p] / len(data)) for p in self.abs_distr]
        self.permissions_name = [p for p in self.abs_distr]
        super().__init__(StaticAppPermissionsDistributionAmongPermissions.name,
                         model,
                         AggregationLevel.APP.iter_instance(model),
                         None,
                         data)

    def compute_data(self, model, filter_non_android_perms):
        data = []
        for app in model.apps:
            permissions = app.permissions
            if filter_non_android_perms:
                permissions = [p for p in permissions if p.startswith("android.permission.")]
            data.append(permissions)
            for p in permissions:
                self.all_permission.add(p)
                self.abs_distr[p] += 1
        return data

    def plot(self):
        permission_distr = [self.abs_distr[p] for p in self.abs_distr]
        df = pd.DataFrame({PD_FRAME_NAME: permission_distr}, index=self.permissions_name)
        data = [
            go.Pie(
                labels=df.index,
                values=df[PD_FRAME_NAME]
            )
        ]

        distr_among_permissions = dcc.Graph(id=self.get_id(),
                                            config=dict(displayModeBar=False),
                                            figure=dict(data=data))

        return distr_among_permissions


def selector_permissions_number(it_unit: Union[BaseExplorationModel],
                                filtering_entries: Callable,
                                aggregation_lvl) -> List[int]:
    return [len(it_unit.app.permissions)]


class StaticPermissionsNumber(MultiNumberUCEComparison):
    """
    Metric assessing the number of permissions.
    """
    description = "Number of permissions"
    name = "Quantity of Permissions"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX, boxpoints='all')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=StaticPermissionsNumber.aggregation_lvls,
                         data_select_op=selector_permissions_number,
                         outlier_method=outlier_method,
                         plot_config=StaticPermissionsNumber.plot_config)


# def selector_receivers_number(it_unit: Union[BaseExplorationModel],
#                               filtering_entries: Callable,
#                               aggregation_lvl) -> List[int]:
#     return [len(app.receivers) for app in model.apps]
#
#
# class StaticReceiversNumber(MultiNumberUCEComparison):
#     """
#     Metric assessing the number of receivers.
#     """
#     description = "Number of receivers"
#     name = "Quantity of Receivers"
#     aggregation_lvls = [AggregationLevel.APP]
#     plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)
#
#     def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
#         super().__init__(model=model,
#                          filtering_op=identity,
#                          aggregation_lvls=StaticReceiversNumber.aggregation_lvls,
#                          data_select_op=selector_receivers_number,
#                          outlier_method=outlier_method,
#                          plot_config=StaticReceiversNumber.plot_config)


# def selector_version_number(it_unit: Union[BaseExplorationModel],
#                                 filtering_entries: Callable,
#                                 aggregation_lvl) -> List[int]:
#     data = []
#     for app in model.apps:
#         if app.version_name.partition(".")[0].isnumeric():
#             data.append(int(app.version_name.partition(".")[0]))
#         else:
#             data.append(1)
#
#     return data
#
#
# class StaticVersionNumber(MultiNumberUCEComparison):
#     """
#     Metric assessing the version number.
#     """
#     description = "Version number (if numeric)"
#     name = "Version Number"
#     aggregation_lvls = [AggregationLevel.APP]
#     plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)
#
#     def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
#         super().__init__(model=model,
#                          filtering_op=identity,
#                          aggregation_lvls=StaticVersionNumber.aggregation_lvls,
#                          data_select_op=selector_version_number,
#                          outlier_method=outlier_method,
#                          plot_config=StaticVersionNumber.plot_config)


def selector_ad_tracking_library_number(it_unit: Union[BaseExplorationModel],
                                        filtering_entries: Callable,
                                        aggregation_lvl) -> List[int]:
    return [len(it_unit.app.ad_tracking_libraries)]


class StaticAdTrackingLibraryNumber(MultiNumberUCEComparison):
    """
    Metric assessing the number of detected ad/tracking libraries.
    """
    description = "Number of detected ad/tracking libraries"
    name = "Quantity of Ad and Tracking Libraries"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX, boxpoints='all')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=StaticAdTrackingLibraryNumber.aggregation_lvls,
                         data_select_op=selector_ad_tracking_library_number,
                         outlier_method=outlier_method,
                         plot_config=StaticAdTrackingLibraryNumber.plot_config)


def selector_package_size(it_unit: Union[BaseExplorationModel],
                          filtering_entries: Callable,
                          aggregation_lvl) -> List[int]:
    return [it_unit.app.app_size]


class StaticPackageSize(MultiNumberUCEComparison):
    """
    Metric assessing the app package size.
    """
    description = "App package size (MB)"
    name = "Package File Size"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX, boxpoints='all')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=StaticPackageSize.aggregation_lvls,
                         data_select_op=selector_package_size,
                         outlier_method=outlier_method,
                         plot_config=StaticPackageSize.plot_config)
