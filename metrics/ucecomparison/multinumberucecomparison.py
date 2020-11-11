# -*- coding: utf-8 -*-
import json
import operator
import os
from abc import ABC
from typing import List, Optional

import dash_core_components as dcc

from aggregationlevel import AggregationLevel
from jsonencoder import MultiNumberUCEComparisonDumpEncoder
from metrics.basedatacache import BaseDataCache
from metrics.datacompound import DataCompound, DataCompoundDump
from metrics.ucecomparison.multinumberucecomparisondump import MultiNumberUCEComparisonDump
from modelaccessor import ModelAccessor
from plot.baseplotter import BasePlotter
from plot.boxplotter import BoxMatplotPlotter
from plotconfiguration import PlotConfiguration, PlotConfigurationDump
from util import configutil, pathutil
from plot import plotutil


class MultiNumberUCEComparison(ModelAccessor, BaseDataCache, ABC):
    def __init__(self,
                 model,
                 filtering_op,
                 data_select_op,
                 aggregation_lvls: List[AggregationLevel],
                 outlier_method,
                 plot_config: Optional[PlotConfiguration] = None,
                 use_case_whitelist=None,
                 force_reload=False):
        super().__init__(model=model)
        self.aggregation_lvls: List[AggregationLevel] = aggregation_lvls
        self.outlier_method = outlier_method()
        self.use_case_whitelist = use_case_whitelist
        self.plot_config: PlotConfiguration = plot_config
        self.data_compounds: List[DataCompound] = self.force_reload_data(model, data_select_op, filtering_op) \
            if force_reload else self.load_data(model, data_select_op, filtering_op)
        self.plotter: BasePlotter = BoxMatplotPlotter()
        self.dump_as_json()

    @staticmethod
    def get_data_compounds_sorted_filtered(data_compounds: List[DataCompound], use_case_whitelist) -> List[
        DataCompound]:
        ls = MultiNumberUCEComparison.get_data_compounds_use_case_sorted_filtered(data_compounds, use_case_whitelist)

        # App level
        dc_app = MultiNumberUCEComparison.get_data_compounds_app(data_compounds)
        if dc_app:
            ls.append(dc_app)

        return ls

    @staticmethod
    def get_data_compounds_use_case_sorted_filtered(data_compounds: List[DataCompound], use_case_whitelist) -> List[
        DataCompound]:
        ls = []
        # UCE level
        uc_lvl_comps = filter(lambda dc: dc.aggregation_lvl == AggregationLevel.USE_CASE, data_compounds)
        if use_case_whitelist is not None:
            uc_lvl_comps = filter(lambda dc: dc.chart_base_title in use_case_whitelist, data_compounds)
        for dc in sorted(uc_lvl_comps, key=operator.attrgetter("chart_base_title")):
            ls.append(dc)

        return ls

    @staticmethod
    def get_data_compounds_app(data_compounds: List[DataCompound]) -> Optional[DataCompound]:
        # App level
        l = list(filter(lambda dc: dc.aggregation_lvl == AggregationLevel.APP, data_compounds))
        return l[0] if l else None

    def title(self):
        return f"{self.description}"

    def compute_data(self, model, data_select_op, filtering_op) -> List[DataCompound]:
        data_compounds = []

        for aggr_lvl in self.aggregation_lvls:
            if aggr_lvl == AggregationLevel.APP:
                # Add app aggregation level data
                data = {}
                for app in model.apps:
                    d = data_select_op(app.exploration_model, filtering_op, aggr_lvl)
                    data[app.package_name] = d
                data_comp = DataCompound(self, "App", data, aggr_lvl, self.outlier_method)
                data_compounds.append(data_comp)
            elif aggr_lvl == AggregationLevel.USE_CASE:
                # Add use case aggregation level data
                use_cases = model.use_case_manager.get_use_cases()
                for use_case in use_cases:
                    data = {}
                    for app in model.apps:
                        if app.exploration_model.use_case_execution_manager.has_use_case(use_case):
                            uce = app.exploration_model.use_case_execution_manager.get_use_case_execution(use_case)
                            d = data_select_op(uce, filtering_op, aggr_lvl)
                            data[app.package_name] = d
                    if data:
                        data_comp = DataCompound(self,
                                                 use_case.name,
                                                 data,
                                                 aggr_lvl,
                                                 self.outlier_method,
                                                 use_case_name=use_case.name)
                        data_compounds.append(data_comp)
            else:
                raise NotImplementedError("Not implemented yet")

        return data_compounds

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def dump_as_json(self):
        if configutil.MATRICS_DUMP_VALUE:
            f_name = f"{self.get_id()}.json"
            path = os.path.join(configutil.MATRICS_DUMP_VALUE_DIR_NAME, f_name)
            with open(path, 'w') as outfile:
                metric_dump = MultiNumberUCEComparisonDump.construct(self)
                json.dump(metric_dump, outfile, cls=MultiNumberUCEComparisonDumpEncoder, indent=4, sort_keys=True)

    def plot(self):
        html_graph_id = self.get_ui_id()
        plot_data = []

        dc_use_cases = MultiNumberUCEComparison.get_data_compounds_use_case_sorted_filtered(self.data_compounds, self.use_case_whitelist)
        dc_app = MultiNumberUCEComparison.get_data_compounds_app(self.data_compounds)
        if dc_app:
            title = dc_app.get_chart_title()
            indices, vals = dc_app.get_data_w_labels()
            plot_data.append((title, indices, vals))

        if dc_use_cases:
            for data_comp in dc_use_cases:
                title = data_comp.get_chart_title()
                indices, vals = data_comp.get_data_w_labels()

                # Filter here use cases that do not contain enough data points
                if len(indices) >= configutil.MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD:
                    plot_data.append((title, indices, vals))

        # graph = plotutil.get_box_subplots(layout_title=self.title(), data=plot_data, axis_type=self.axis_type)
        data, layout = plotutil.get_box_plots_config(layout_title=self.title(), data=plot_data, plot_config=self.plot_config)
        graph = dcc.Graph(id=html_graph_id, config=dict(displayModeBar=False), figure=dict(data=data, layout=layout))

        # TODO
        plotutil.write_plot_to_file(data, layout, f"{html_graph_id}")
        # self.persist_plot(self.title(), dc_use_cases, dc_app, self.plot_config)

        return graph

    def persist_plot(self, title, dc_use_cases, dc_app, plot_config):
        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plot_id = self.get_ui_id()
            target_f = pathutil.get_figure_image_path(plot_id)
            dcs = []
            if dc_use_cases:
                dcs.extend(dc_use_cases)
            if dc_app:
                dcs.append(dc_app)
            if dcs:
                self.plotter.plot_data_compounds(title, dcs, target_f, plot_config)
                # plotutil.write_plot_to_file(data, layout, f"{plot_id}-{plot_config.univariate_plot_style.value}")

    # def plot(self):
    #     html_graph_id = self.get_ui_id()
    #     plot_data = []
    #
    #     dc_app = MultiNumberUCEComparison.get_data_compounds_app(self.data_compounds)
    #     if dc_app:
    #         prefix = dc_app.chart_base_title
    #         title, indices, vals = dc_app.get_data_w_labels()
    #         plot_data.append((title, indices, vals))
    #
    #     dc_use_cases = MultiNumberUCEComparison.get_data_compounds_use_case_sorted_filtered(self.data_compounds, self.use_case_whitelist)
    #     if dc_use_cases:
    #         for data_comp in dc_use_cases:
    #             prefix = f"Use Case ({data_comp.chart_base_title})"
    #             title, indices, vals = data_comp.get_data_w_labels()
    #
    #             # Filter here use cases that do not contain enough data points
    #             if len(indices) >= DATAPOINT_THRESHOLD:
    #                 plot_data.append((title, indices, vals))
    #
    #     data, layout = plotutil.get_box_plots(layout_title=self.title(), data=plot_data, axis_type=self.axis_type)
    #
    #     if configutil.MATRICS_FIGURE_DUMP_PLOTS:
    #         plotutil.write_plot_to_file(data, layout, f"{html_graph_id}-uce-{self.plot_config.univariate_plot_style.value}")
    #
    #     return dcc.Graph(id=html_graph_id, config=dict(displayModeBar=False), figure=dict(data=data, layout=layout))

    def get_data_compounds(self) -> List[DataCompound]:
        return MultiNumberUCEComparison.get_data_compounds_sorted_filtered(self.data_compounds, self.use_case_whitelist)
