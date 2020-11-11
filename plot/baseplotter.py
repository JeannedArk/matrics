# -*- coding: utf-8 -*-
import json
from abc import ABCMeta, abstractmethod
from typing import Tuple, List

from metrics.datacompound import DataCompound, DataCompoundDump
from metrics.ucecomparison.multinumberucecomparisondump import MultiNumberUCEComparisonDump
from plotconfiguration import PlotConfiguration
from util import configutil

# TODO probably remove plot configuration


class BasePlotter(metaclass=ABCMeta):
    @abstractmethod
    def plot_data_compound(self, title, dc: DataCompoundDump, target_f, plot_config: PlotConfiguration, show=False):
        pass

    @abstractmethod
    def plot_data_compounds(self, title, dcs: List[DataCompoundDump], target_f, plot_config: PlotConfiguration, show=False):
        pass

    def plot(self, json_f, target_f, plot_config: PlotConfiguration):
        with open(json_f, newline='') as f:
            metric_json = json.load(f)
            metric = MultiNumberUCEComparisonDump.construct_from_json(metric_json)
            data_comps = [dc for dc in metric.data_compounds
                          if len(self.get_data(dc)) >= configutil.MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD]
            self.plot_data_compounds(metric.description,
                                     data_comps,
                                     target_f,
                                     metric.plot_config,
                                     show=True)

    def get_data_w_labels(self, data, prefix) -> Tuple[str, List, List]:
        indices = []
        vals = []
        items = data.items()
        app_package_names_w_valid_data = set()
        for app_package_name, data in items:
            if type(data) == list:
                app_package_names_w_valid_data.add(app_package_name)
                for d in data:
                    indices.append(app_package_name)
                    vals.append(d)
        assert len(indices) == len(vals), f"Indices: {len(indices)} Vals: {len(vals)}"

        title = DataCompound.get_info_header(prefix, vals, app_package_names_w_valid_data)

        return title, indices, vals

    def get_data_w_title(self, data, prefix) -> Tuple[str, List]:
        vals = []
        items = data.items()
        app_package_names_w_valid_data = set()
        for app_package_name, data in items:
            if type(data) == list:
                app_package_names_w_valid_data.add(app_package_name)
                for d in data:
                    vals.append(d)

        title = DataCompound.get_info_header(prefix, vals, app_package_names_w_valid_data)

        return title, vals

    def get_data(self, dc: DataCompoundDump) -> List:
        vals = []
        items = dc.data.items()
        app_package_names_w_valid_data = set()
        for app_package_name, data in items:
            if type(data) == list:
                app_package_names_w_valid_data.add(app_package_name)
                for d in data:
                    vals.append(d)

        return vals

    def should_plot(self, dc: DataCompoundDump) -> bool:
        return len(self.get_data(dc)) >= configutil.MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD
