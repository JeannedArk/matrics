# -*- coding: utf-8 -*-
import operator
from typing import List, Any

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_table
import numpy as np
import pandas as pd
import plotly.graph_objs as go

import colorconstants
from metrics.basedatacache import BaseDataCache
from modelaccessor import ModelAccessor
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector
from plotconfiguration import PlotStyle
from util import configutil, tableutil
from plot import plotutil
from util.latexutil import texify, bool_to_latex_str
from util.modelutil import calculate_use_case_matrix
from util.uiutil import header_metric


USE_CASE_STATE_COMPUTED = "COMPUTED"
USE_CASE_STATE_VERIFIED = "VERIFIED"
USE_CASE_STATE_DEFINED_FOR_APP = "DEFINED"

USE_CASE_EXECUTIONS_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID = "use-case-executions-overview-stacked-bar-chart-graph"
USE_CASE_EXECUTIONS_COMPUTED_VERIFIED_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID = "use-case-executions-computed-verified-overview-grouped-bar-chart-graph"


class AppsUseCaseExecutionsOverview(ModelAccessor, BaseDataCache):
    description = "Use Case Overview"

    def __init__(self,
                 model=None,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model)
        self.outlier_method = outlier_method

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def get_data_compounds(self):
        return []

    def compute_data(self, *args, **kwargs) -> Any:
        pass

    def plot(self):
        data = {
            "App": [],
            "Verified UCEs": [],
        }
        apps = self.model.get_apps_sorted()
        for app in apps:
            uces = sorted(app.exploration_model.use_case_execution_manager.get_verified_use_case_executions(),
                          key=operator.attrgetter("use_case.name"))
            if uces:
                data["App"].append(app.package_name)
                data["Verified UCEs"].append(", ".join(uce.use_case.name for uce in uces))

        df = pd.DataFrame(data, columns=data.keys())
        return tableutil.create_table_html(df)


class UseCaseExecutionsAppsOverview(ModelAccessor, BaseDataCache):
    description = "Use Case Overview"

    def __init__(self,
                 model=None,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model)
        self.outlier_method = outlier_method

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def get_data_compounds(self):
        return []

    def compute_data(self, *args, **kwargs) -> Any:
        pass

    def plot(self):
        data = {
            "Use Case": [],
            "Apps with verified UCE": [],
        }
        apps = sorted(self.model.apps)
        for use_case in sorted(self.model.use_case_manager.get_use_cases(), key=operator.attrgetter('name')):
            apps_use_case = [app for app in apps
                             if app.exploration_model.use_case_execution_manager.has_use_case(use_case, ignore_playback_state=False)]
            if apps_use_case:
                data["Use Case"].append(use_case.name)
                data["Apps with verified UCE"].append(", ".join(app.package_name for app in apps_use_case))

        df = pd.DataFrame(data, columns=data.keys())
        return tableutil.create_table_html(df)


class UseCaseOverview(ModelAccessor, BaseDataCache):
    description = "Use Case Overview"

    def __init__(self,
                 model=None,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model)
        self.outlier_method = outlier_method

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def get_data_compounds(self):
        return []

    def plot(self):
        html_elements = []

        apps = sorted(self.model.apps)
        matrix = self.load_data(apps)

        df = pd.DataFrame(
            {
                'domain': [app.domain for app in apps],
                'package_name': [app.package_name for app in apps],
                'app': apps
            }
        )

        by_domain = df.groupby("domain")
        for domain, frame in by_domain:
            domain_apps = [app for app in frame["app"]]
            use_cases = sorted(
                [use_case.name for use_case in self.model.use_case_manager.get_use_cases_for_domain(domain)])
            html_elements.append(header_metric(f"Use Case Overview: {domain.value}"))
            dt = self.get_overview_table(domain_apps, use_cases, matrix)
            html_elements.append(dt)

        bar_plots, layout = self.get_verified_use_case_execution_stacked_bar_charts(apps, matrix)
        html_elements.append(header_metric("Use Case Executions Overview Stacked Bar Chart: Distribution of apps among verified use case executions"))
        graph = dcc.Graph(id=USE_CASE_EXECUTIONS_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID,
                          config=dict(displayModeBar=False),
                          figure=dict(data=bar_plots, layout=layout))
        html_elements.append(graph)

        bar_plots, layout = self.get_number_computed_verified_grouped_bar_chart(apps, matrix)
        html_elements.append(header_metric("Use Case Executions Computed Verified Overview Stacked Bar Chart"))
        graph = dcc.Graph(id=USE_CASE_EXECUTIONS_COMPUTED_VERIFIED_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID,
                          config=dict(displayModeBar=False),
                          figure=dict(data=bar_plots, layout=layout))
        html_elements.append(graph)

        return dbc.Container(id=self.get_ui_id(), children=html_elements)

    def compute_data(self, apps):
        return calculate_use_case_matrix(apps, self.model)

    def get_number_computed_verified_grouped_bar_chart(self, apps, matrix):
        use_cases = sorted((use_case.name for use_case in self.model.use_case_manager.get_use_cases()), reverse=True)
        use_cases_comp_or_ver = [use_case for use_case in use_cases
                                 if sum(1 for app in apps if matrix[app.package_name][use_case][USE_CASE_STATE_COMPUTED])
                                 + sum(1 for app in apps if matrix[app.package_name][use_case][USE_CASE_STATE_VERIFIED]) > 0]

        bars = []
        settings = {
            "computed": { "key": USE_CASE_STATE_COMPUTED, "color": "blue" },
            "verified": { "key": USE_CASE_STATE_VERIFIED, "color": "orange" },
        }

        marker_lines = []
        for name, config in settings.items():
            key = config["key"]
            color = config["color"]
            data = [sum(1 for app in apps if matrix[app.package_name][use_case][key])
                    for use_case in use_cases_comp_or_ver]
            nparr = np.array(data)
            bar = go.Bar(
                # x=use_cases_comp_or_ver,
                # y=data,
                x=data,
                y=use_cases_comp_or_ver,
                textposition='auto',
                name=name,
                marker_color=color,
                orientation='h',
            )

            bars.append(bar)

            # Draw mean
            outlier_method = ZScore1StdDevOutlierDetector()
            outlier_method.init(nparr)
            marker_val = outlier_method.marker_value()
            marker_line = {
                'type': 'line',
                # 'x0': -0.5,
                # 'y0': marker_val,
                # 'x1': nparr.size - 0.5,
                # 'y1': marker_val,
                'x0': marker_val,
                'y0': -0.5,
                'x1': marker_val,
                'y1': nparr.size - 0.5,
                'xref': 'x',
                'yref': 'y',
                'line': {
                    'color': color,
                    'width': 2,
                    'dash': configutil.MATRICS_FIGURE_DASH_STYLE,
                },
            }
            marker_lines.append(marker_line)

        height = plotutil.get_height_for_vertical_extendable_plots(len(use_cases_comp_or_ver), PlotStyle.BAR)
        layout = go.Layout(
            # title="Distribution of apps among verified use case executions",
            height=height,
            xaxis=dict(
                automargin=True,
                title="#Use case executions",
                dtick=2,
                # "tickangle": 50,
            ),
            yaxis=dict(
                automargin=True,
                dtick=1,
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            barmode='group',
            shapes=marker_lines,
            font=dict(
                size=configutil.MATRICS_FIGURE_FONT_SIZE,
                family=configutil.MATRICS_FIGURE_FONT_FAMILY,
            ),
        )

        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_plot_to_file(bars, layout,
                                        USE_CASE_EXECUTIONS_COMPUTED_VERIFIED_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID,
                                        width=600)

        return bars, layout

    def get_verified_use_case_execution_stacked_bar_charts(self, apps, matrix):
        use_cases_verified = self.get_only_verified_use_cases(apps, matrix)
        use_cases_verified_set = set(use_cases_verified)
        use_cases_computed = set(self.get_only_computed_use_cases(apps, matrix))
        use_cases_all = set(use_case.name for use_case in self.model.use_case_manager.get_use_cases())
        # print(f"Use cases all: {len(use_cases_all)}  Use cases computed: {len(use_cases_computed)}  Use cases verified: {len(use_cases_verified_set)}")
        # print(f"Computed use cases percentage from all: {len(use_cases_computed) / len(use_cases_all)}")
        # print(f"Verified use cases percentage from all: {len(use_cases_verified_set) / len(use_cases_all)}")
        # print(f"Verified use cases percentage from computed: {len(use_cases_verified_set) / len(use_cases_computed)}")

        df = pd.DataFrame(
            {
                'domain': [app.domain for app in apps],
                'package_name': [app.package_name for app in apps],
                'app': apps
            }
        )

        bars = []
        by_domain = df.groupby("domain")
        for domain, frame in by_domain:
            domain_apps = [app for app in frame["app"]]
            data = [sum(1 for app in domain_apps if matrix[app.package_name][use_case][USE_CASE_STATE_VERIFIED])
                    for use_case in use_cases_verified]
            percentage_of_apps_of_domain = [f"{d / len(domain_apps)}%" for d in data]
            bar = go.Bar(
                x=data,
                y=use_cases_verified,
                text=percentage_of_apps_of_domain,
                textposition='auto',
                name=domain.value,
                orientation='h',
            )

            bars.append(bar)

        height = plotutil.get_height_for_vertical_extendable_plots(len(use_cases_verified), PlotStyle.BAR)
        layout = go.Layout(
            # title="Distribution of apps among verified use case executions",
            height=height,
            xaxis=dict(
                automargin=True,
                title="#Verified use case executions",
                # "tickangle": 50,
            ),
            yaxis=dict(
                automargin=True,
                dtick=1,
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            barmode='stack',
            font=dict(
                size=configutil.MATRICS_FIGURE_FONT_SIZE,
                family=configutil.MATRICS_FIGURE_FONT_FAMILY,
            ),
        )

        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_plot_to_file(bars, layout, USE_CASE_EXECUTIONS_OVERVIEW_STACKED_BAR_CHART_GRAPH_ID,
                                        width=600)

        return bars, layout

    def get_only_verified_use_cases(self, apps, matrix) -> List[str]:
        use_case_names = []
        for use_case in self.model.use_case_manager.get_use_cases():
            s = sum(1 for app in apps if matrix[app.package_name][use_case.name][USE_CASE_STATE_VERIFIED])
            if s > 0:
                use_case_names.append(use_case.name)

        return sorted(use_case_names, reverse=True)

    def get_only_computed_use_cases(self, apps, matrix) -> List[str]:
        use_case_names = []
        for use_case in self.model.use_case_manager.get_use_cases():
            s = sum(1 for app in apps if matrix[app.package_name][use_case.name][USE_CASE_STATE_COMPUTED])
            if s > 0:
                use_case_names.append(use_case.name)

        return sorted(use_case_names, reverse=True)

    def get_overview_table(self, apps, use_cases, matrix):
        data = [self.get_column_data(use_case, apps, matrix) for use_case in use_cases]
        style_data_conditional = [] +\
        [self.get_style_conditional(f"app {app.package_name} computed", f'{{app {app.package_name} computed}} eq "True"') for app in apps] +\
        [self.get_style_conditional(f"app {app.package_name} verified", f'{{app {app.package_name} verified}} eq "True"') for app in apps]

        # self.print_latex_table(apps, use_cases, matrix)

        dt = dash_table.DataTable(
            data=data,
            columns=self.get_columns(apps),
            style_cell={
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': colorconstants.RGB_COLOR_LIGHT_GREY,
            },
            merge_duplicate_headers=True,
            style_data_conditional=style_data_conditional,
        )

        return dt

    def get_style_conditional(self, column_id, filter_query):
        style_data_conditional = {
            'if': {
                'column_id': column_id,
                'filter_query': filter_query
            },
            'backgroundColor': colorconstants.HEX_COLOR_DARK_GREEN,
            'color': 'white',
        }
        return style_data_conditional

    def get_columns(self, apps):
        columns = [{"name": ["", "", "", "Use Case"], "id": "use case"}]
        for app in apps:
            columns.append({"name": ["Apps", app.domain.value, app.package_name, "Computed"], "id": f"app {app.package_name} computed"})
            columns.append({"name": ["Apps", app.domain.value, app.package_name, "Verified"], "id": f"app {app.package_name} verified"})
        return columns

    def get_column_data(self, use_case, apps, matrix):
        d = { "use case": use_case }
        for app in apps:
            d[f"app {app.package_name} computed"] = str(matrix[app.package_name][use_case][USE_CASE_STATE_COMPUTED])
            d[f"app {app.package_name} verified"] = str(matrix[app.package_name][use_case][USE_CASE_STATE_VERIFIED])
        return d

    def print_latex_table(self, apps, use_cases, matrix):
        print(f"\n>>>>>>>>>>>>>> Use Case Overview Computed Verified Table\n")
        begin_tabular_str = " ".join("c c" for app in apps)
        print(f"\\begin{{tabular}}{{l {begin_tabular_str}}}")
        print("\\hline")
        header = " & ".join([f"\\multicolumn{{2}}{{c}}{{{app.short_name}}}" for app in apps])
        # \multirow{2}{*}{Use Case} & \multicolumn{2}{c}{com.reddit.frontpage} & \multicolumn{2}{c}{com.tumblr} \\
        print(f"\\multirow{{2}}{{*}}{{Use Case}} & {header} \\\\")
        print(f"\\cline{{2-{2 * len(apps) + 1}}}")
        computed_verified_header = " & ".join(f"C & V" for app in apps)
        print(f"& {computed_verified_header} \\\\")
        print("\\hline")
        for use_case in use_cases:
            use_case_str = texify(use_case)
            row = " & ".join([f"{bool_to_latex_str(matrix[app.package_name][use_case][USE_CASE_STATE_COMPUTED])} & {bool_to_latex_str(matrix[app.package_name][use_case][USE_CASE_STATE_VERIFIED])}"
                              for app in apps])
            print(f"{use_case_str} & {row} \\\\")

        print("\\end{tabular}")