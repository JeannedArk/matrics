# -*- coding: utf-8 -*-
import operator
import os
from typing import List
import numpy as np

from tqdm import tqdm

from aggregationlevel import AggregationLevel
from metrics.datacompound import DataCompound
from metrics.modelaccessorsets import MODEL_ACCESSORS_ALL, METRICS_STATIC, METRICS_BASIC
from metrics.metric import *
from model.androidapp import App
from outlierdetection import univariateoutlierdetection
from plotconfiguration import PlotConfiguration, PlotStyle
from usecaseclassification.usecasemanager import UseCaseManager
from util import configutil, statisticsutil
from util.configutil import MATRICS_CFG_APP_FILTER_LIST, MATRICS_CFG_MODEL_ACCESSOR_SELECTION
from util.latexutil import texify


class Model(object):

    sorted_metrics_list = [
        "Quantity of Nodes",
        "Quantity of Edges",
        "Node Connectivity",
        "Edge Connectivity",
        "Depth from Home Screen",
        "Density",
        "Quantity of Features",
        "Quantity of UCEs",
        "Quantity of Computed UCEs",
        "Quantity of Verified UCEs",
        "Quantity of GUI Elements",
        "Quantity of Buttons",
        "Size of Buttons",
        "Quantity of Network Requests",
        "Latency of Network Requests",
        "Payload Size of Network Requests",
        "Payload Size of Network Responses",
        "Quantity of Network Errors",
        "Quantity of Permissions",
        "Quantity of Ad and Tracking Libraries",
        "Quantity of Crashes",
        "Play Store Rating",
        "Play Store Quantity of Reviews",
        "Play Store Quantity of Installations",
    ]

    def __init__(self, apps: List[App], config_togape, matrics_config, univariate_outlier_method):
        self.apps: List[App] = apps
        self.config_togape = config_togape
        self.matrics_config = matrics_config
        self.univariate_outlier_method = univariate_outlier_method
        self.plot_config: PlotConfiguration = self.get_plot_config()
        self.model_accessors = {}
        self.atd_path = config_togape[configutil.TOGAPE_CFG_ATD_PATH]
        self.use_case_manager = UseCaseManager(self.atd_path)

    def get_apps_sorted(self):
        return sorted(self.apps, key=operator.attrgetter('package_name'))

    def get_apps_sorted_like_in_thesis(self):
        apps = sorted(self.apps, key=operator.attrgetter('package_name'))
        apps = sorted(apps, key=operator.attrgetter('domain'))
        return apps

    def get_plot_config(self):
        plot_style = None
        # Only use the box plot if the univariate method is IQR.
        if self.univariate_outlier_method.name == univariateoutlierdetection.IQROutlierDetector.name:
            plot_style = PlotStyle.BOX
        else:
            plot_style = PlotStyle.BAR
        return PlotConfiguration(univariate_plot_style=plot_style, axis_type="linear")

    def construct_metrics(self):
        """
        We could parallelize this step, if it takes too much time.
        """
        model_accessors_ls = MODEL_ACCESSORS_ALL if MATRICS_CFG_MODEL_ACCESSOR_SELECTION not in self.matrics_config else self.matrics_config[MATRICS_CFG_MODEL_ACCESSOR_SELECTION]
        model_accessors = {}
        for m in tqdm(model_accessors_ls, desc="Metrics"):
            # print(f"Model accessor: {m}")
            m_: ModelAccessor = m(model=self, outlier_method=self.univariate_outlier_method)
            model_accessors[m_.get_id()] = m_

        self.model_accessors = model_accessors

        self.print_latex()

    def get_all_data_compounds_with_sane_data(self) -> List[DataCompound]:
        dcs = [dc for model_acc in self.model_accessors.values() for dc in model_acc.get_data_compounds() if
                 dc.get_data() is not None and all(np.isreal(d) and np.isscalar(d) for d in dc.get_data())]
        return self.sort_data_compounds(dcs)

    def sort_data_compounds(self, dcs: List[DataCompound]) -> List[DataCompound]:
        return list(sorted(dcs,
                           key=lambda dc: Model.sorted_metrics_list.index(dc.get_name())
                           if dc.get_name() in Model.sorted_metrics_list else 1000))

    def print_latex(self):
        # print(f"\n>>>>>>>>>>>>>> Latex Data\n")
        # for app in self.apps:
        #     app.exploration_model.use_case_base_transformed_graph.merger.print_latex_table()
        self.print_metrics_descriptive_statistics_latex_table()
        # self.print_metrics_outlier_statistics_latex_table()
        # self.print_app_home_state_table()
        # self.print_coef_quartile_variation_latex_table()
        # self.print_playback_results()
        pass

    def print_app_home_state_table(self):
        print(f"\n>>>>>>>>>>>>>> App Home State Tag Table\n")
        print(f"Domain & App Reference Name & Distance of Tagged State to Correct State & Tagging Method \\\\")
        distances = []
        for app in self.get_apps_sorted_like_in_thesis():
            dist = app.exploration_model.app_home_state_tag_manager.calc_distance()
            distances.append(dist)
            tagging_method = app.exploration_model.app_home_state_tag_manager.get_tagging_method().value
            print(f" & {app.short_name} & {dist} & {tagging_method} \\\\")
        avg_dist = np.mean(distances)
        print(f"Statistics: sum dist: {sum(distances)} avg dist: {avg_dist}")

    def print_metrics_descriptive_statistics_latex_table(self):
        print(f"\n>>>>>>>>>>>>>> Descriptive statistics table\n")
        print(f"Metric Name & Aggregation Level & {statisticsutil.descriptive_statistics_latex_header()} \\\\")

        rejected_metrics = []

        for dc in self.get_all_data_compounds_with_sane_data():
            data = dc.get_data()
            name = texify(dc.get_name())
            aggr_txt = texify(dc.get_aggregation_level_str())
            if len(data) >= configutil.MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD:
                s = statisticsutil.descriptive_statistics_latex_row(dc.get_data())
                print(f"{name} & {aggr_txt} & {s} \\\\")
            else:
                rejected_metrics.append(f"{name} {aggr_txt}")

        print(f"\n\nRejected metrics:")
        for metric in rejected_metrics:
            print(metric)

    def print_metrics_outlier_statistics_latex_table(self):
        print(f"\n>>>>>>>>>>>>>> Metrics outlier statistics table\n")
        print(f"Category & Metric Name & Aggregation Level & Sample Size & Coefficient of Variance & \\#Outliers \\\\")

        SAMPLE_SIZE_THRESHOLD = 4
        CV_THRESHOLD = 0.6
        DETECTED_OUTLIER_NUM_THRESHOLD = 1

        rejected_metrics = []

        for dc in self.get_all_data_compounds_with_sane_data():
            name = texify(dc.get_name())
            aggr_lvl = dc.get_aggregation_level()
            if aggr_lvl == AggregationLevel.USE_CASE:
                aggr_lvl_tex = f"\\ac{{UCE}}: {texify(dc.use_case_name)}"
            else:
                aggr_lvl_tex = texify(aggr_lvl.texify())

            data = dc.get_data()
            sample_size = len(data)
            sample_size_tex = texify(sample_size)
            coeff_var_num = statisticsutil.coeff_variance(data)
            coeff_var = texify(statisticsutil.coeff_variance(data))
            coeff_var_tex = "" if coeff_var == "NaN" else coeff_var
            num_outliers = len(dc.outlier_method.outliers()) if sample_size >= SAMPLE_SIZE_THRESHOLD else 0
            num_outliers_tex = num_outliers if num_outliers <= 0 else f"\\textbf{{{num_outliers}}}"
            assert coeff_var != "NaN" or (coeff_var == "NaN" and num_outliers == 0)

            print_crit = False
            if sample_size >= SAMPLE_SIZE_THRESHOLD:
                if num_outliers >= DETECTED_OUTLIER_NUM_THRESHOLD:
                    print_crit = True
            else:
                if coeff_var_num >= CV_THRESHOLD:
                    print_crit = True

            if print_crit:
                print(f"& {name} & {aggr_lvl_tex} & {sample_size_tex} & {coeff_var_tex} & {num_outliers_tex} \\\\")
            else:
                rejected_metrics.append(f"{name} {aggr_lvl_tex}")

        print(f"\n\nRejected metrics:")
        for metric in rejected_metrics:
            print(metric)

    def print_coef_quartile_variation_latex_table(self):
        print(f"\n>>>>>>>>>>>>>> Metrics coefficient of quartile variation table\n")
        print(f"Category & Metric Name & Aggregation Level & \\ac{{CQV}} \\\\")

        for dc in self.get_all_data_compounds_with_sane_data():
            data = dc.get_data()
            name = texify(dc.get_name())
            aggr_txt = texify(dc.get_aggregation_level_str())
            if len(data) >= configutil.MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD:
                coef = texify(statisticsutil.coeff_quartile_variation(dc.get_data()))
                print(f"& {name} & {aggr_txt} & {coef} \\\\")

    def print_playback_results(self):
        print(f"\n>>>>>>>>>>>>>> Playback results\n")
        total = 0
        playback_succ_total = 0
        for app in self.get_apps_sorted_like_in_thesis():
            playback_succ, playback_fail = app.exploration_model.use_case_execution_manager.get_playback_statistics()
            total += playback_succ + playback_fail
            playback_succ_total += playback_succ
        print(f"Number of total playbacks: {total} Number of successful playbacks: {playback_succ_total}")
