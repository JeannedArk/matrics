# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from abc import ABCMeta, ABC
import dash_core_components as dcc

from metrics.basedatacache import BaseDataCache
from metrics.metricsconstructionexception import MetricsConstructionException
from modelaccessor import ModelAccessor

from aggregationlevel import BaseAggregationLevelIterator
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector
from plotconfiguration import PlotConfiguration, PlotStyle
from util import configutil, statisticsutil
from plot import plotutil
from util.util import shorten_fl


def data_frame_mean(df, id): return df[id].mean()
def data_frame_max(df, id): return df[id].max()


def identity(x): return x
def to_set(x): return set(x)


class BaseMetric(ModelAccessor, BaseDataCache, metaclass=ABCMeta):
    def __init__(self,
                 name: str,
                 model,
                 aggregation_level_it: BaseAggregationLevelIterator,
                 outlier_method,
                 data):
        super().__init__(model)
        self.name = name
        self.app_names = [app.package_name for app in model.apps]
        self.aggregation_level_it = aggregation_level_it
        self.outlier_method = outlier_method
        self.plot_config: PlotConfiguration = model.plot_config
        self.data = data

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def title(self):
        return f"{self.description}, Aggr. level: {self.get_title()}"

    def get_aggregation_level(self):
        return self.aggregation_level_it.aggregation_level

    def get_title(self):
        return self.aggregation_level_it.title()

    def get_data_compounds(self):
        return []


# TODO change that
PD_FRAME_NAME = "frame"


class BaseSingleEntryMetric(BaseMetric, ABC):
    """
    Abstract class for metrics employing only one decimal value per app.
    """
    def __init__(self,
                 name,
                 model,
                 data,
                 aggregation_level_it,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(name, model, aggregation_level_it, outlier_method(), data)
        self.nparr: np.ndarray = np.array(self.data)
        if len(aggregation_level_it.get_indices()) <= 1:
            raise MetricsConstructionException(f"Indices must be larger than 1, was {aggregation_level_it.get_indices()}")
        self.df = pd.DataFrame({PD_FRAME_NAME: self.nparr}, index=aggregation_level_it.get_indices())
        self.outlier_method.init(self.nparr)

    def plotly(self, yaxis_type):
        plot = None
        if self.plot_config.univariate_plot_style == PlotStyle.BOX:
            pd_sorted = self.df.sort_values(by=[PD_FRAME_NAME])
            plot = plotutil.get_box_plot(values=pd_sorted[PD_FRAME_NAME],
                                         indices=pd_sorted.index,
                                         layout_title=self.title(),
                                         box_title=f"Metric: {self.get_id()}",
                                         axis_type=yaxis_type)
        elif self.plot_config.univariate_plot_style == PlotStyle.BAR:
            pd_sorted = self.df.sort_values(by=[PD_FRAME_NAME])
            plot = plotutil.get_bar_plot(indices=pd_sorted.index,
                                         outlier_method=self.outlier_method,
                                         values=pd_sorted[PD_FRAME_NAME],
                                         layout_title=self.title(),
                                         bar_title=f"Metric: {self.get_id()}",
                                         yaxis_type=yaxis_type)
        else:
            raise RuntimeError(f"Unknown plot style: {self.plot_config.univariate_plot_style}")
        return plot

    def plot(self, html_graph_id=None, yaxis_type="linear"):
        """
        :param html_graph_id: This parameter is passed by the MetricAggregator.
        """
        html_graph_id = html_graph_id if html_graph_id is not None else self.get_ui_id()
        data, layout = self.plotly(yaxis_type=yaxis_type)
        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_plot_to_file(data, layout, f"{html_graph_id}-{self.plot_config.univariate_plot_style.value}")
        return dcc.Graph(id=html_graph_id,
                         config=dict(displayModeBar=False),
                         figure=dict(data=data, layout=layout))

    def len(self):
        return len(self.data)


class SingleNumberMetric(BaseSingleEntryMetric):
    description = ""

    def __init__(self,
                 name,
                 model,
                 filtering_op,
                 data_op,
                 data_select_op,
                 aggregation_lvl_it: BaseAggregationLevelIterator,
                 description,
                 outlier_method):
        """
        :param model:
        :param filtering_op: function to filter for objects that are generated from data_select_op,
        e.g. only interactable widgets
        :param data_select_op: TODO
        :param data_op: determines the data operation on the data frame, e.g. max or mean
        :param aggregation_lvl_it: TODO
        :param description: the description that will be displayed in the result plot
        """
        self.description = description
        self.cache_load_id = f"{self.get_id()}-{name}-{data_op.__name__}-{aggregation_lvl_it.title()}"\
            .replace("(", "").replace(")", "").replace(" ", "-").lower()
        # Additionally, we store/load the indices, because in the load phase we skip compute_data and lose
        # information which indices we should use
        data, aggregation_lvl_it_indices = self.load_data(filtering_op, data_op, data_select_op, aggregation_lvl_it)
        aggregation_lvl_it.set_indices(aggregation_lvl_it_indices)
        super().__init__(name, model, data, aggregation_lvl_it, outlier_method)

    def compute_data(self, filtering_op, data_op, data_select_op, aggregation_lvl_it: BaseAggregationLevelIterator):
        data = []
        aggregation_level = aggregation_lvl_it.aggregation_level
        pd_entry = "entry"
        for i, it_unit in enumerate(aggregation_lvl_it.iter()):
            try:
                tmp = data_select_op(filtering_op, data_op, it_unit, aggregation_level)
                df = pd.DataFrame({pd_entry: tmp})
                tmp = data_op(df, pd_entry)
                assert not np.isnan(tmp), f"Result of data_op was invalid: {tmp}"
                data.append(tmp)
                aggregation_lvl_it.add_index(i)
            except MetricsConstructionException as e:
                # Noop: Skip that iteration unit, data is not useful
                pass
        # Additionally return the indices
        return data, aggregation_lvl_it.get_indices()

    def get_cache_load_id(self) -> str:
        """
        Override the function because in the case of the MetricAggregator this class
        gets directly instantiated and the super implementation does not have any means
        to distinguish between these instantiations.
        """
        return self.cache_load_id


class MultiNumberMetric(ModelAccessor, BaseDataCache):
    description = ""

    def __init__(self,
                 name,
                 model,
                 filtering_op,
                 data_select_op,
                 aggregation_lvl_it: BaseAggregationLevelIterator,
                 description,
                 outlier_method,
                 axis_type="linear",):
        """
        :param model:
        :param filtering_op: function to filter for objects that are generated from data_select_op,
        e.g. only interactable widgets
        :param data_select_op: TODO
        :param aggregation_lvl_it: TODO
        :param description: the description that will be displayed in the result plot
        """
        super().__init__(name)
        self.description = description
        self.outlier_method = outlier_method()
        self.aggregation_level_it = aggregation_lvl_it
        self.axis_type = axis_type
        self.plot_config: PlotConfiguration = model.plot_config
        self.cache_load_id = f"{self.get_id()}-{name}-{aggregation_lvl_it.title()}-multi"\
            .replace("(", "").replace(")", "").replace(" ", "-").lower()
        # Additionally, we store/load the indices, because in the load phase we skip compute_data and lose
        # information which indices we should use
        data, aggregation_lvl_it_indices = self.load_data(filtering_op, data_select_op, aggregation_lvl_it)
        aggregation_lvl_it.set_indices(aggregation_lvl_it_indices)
        self.data = data
        # self.df = pd.DataFrame(self.data)

    def get_cache_load_id(self) -> str:
        """
        Override the function because in the case of the MetricAggregator this class
        gets directly instantiated and the super implementation does not have any means
        to distinguish between these instantiations.
        """
        return self.cache_load_id

    def title(self):
        data = []
        # data = itertools.chain.from_iterable(d for d in self.data)
        return f"{self.description}, Aggr. level: {self.get_title()}, CV: {shorten_fl(statisticsutil.coeff_variance(data))}"

    def get_title(self):
        return self.aggregation_level_it.title()

    def get_data_compounds(self):
        return []

    def compute_data(self, filtering_op, data_select_op, aggregation_lvl_it: BaseAggregationLevelIterator):
        data = {}
        aggregation_level = aggregation_lvl_it.aggregation_level
        for i, it_unit in enumerate(aggregation_lvl_it.iter()):
            try:
                data[i] = data_select_op(filtering_op, None, it_unit, aggregation_level)
                aggregation_lvl_it.add_index(i)
            except MetricsConstructionException as e:
                # Noop: Skip that iteration unit, data is not useful
                pass
        # Additionally return the indices
        return data, aggregation_lvl_it.get_indices()

    def plot(self, html_graph_id=None):
        html_graph_id = html_graph_id if html_graph_id is not None else self.get_ui_id()
        values = []
        indices = []

        for idx, idx_vals in self.data.items():
            package_name = self.aggregation_level_it.get_index(idx)
            for item in idx_vals:
                indices.append(package_name)
            print(package_name)
            print(idx_vals)
            values.extend(idx_vals)
            # values.append((idx, items))

        data, layout = plotutil.get_box_plot(layout_title=self.title(),
                                             box_title=f"Metric: {self.get_id()}",
                                             values=values,
                                             indices=indices,
                                             axis_type=self.axis_type)
        # data, layout = plotutil.get_violin_plots(layout_title=self.title(), data=plot_data)
        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_plot_to_file(data, layout, f"{html_graph_id}-{self.plot_config.univariate_plot_style.value}")
        return dcc.Graph(id=html_graph_id,
                         config=dict(displayModeBar=False),
                         figure=dict(data=data, layout=layout))
