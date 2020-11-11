# -*- coding: utf-8 -*-
import plotly.graph_objs as go
from typing import Callable, List, Union
import dash_core_components as dcc

from aggregationlevel import AggregationLevel
from metrics.metric import identity, BaseSingleEntryMetric
from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel
from model.explorationmodel import ExplorationModel
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector
from plotconfiguration import PlotConfiguration, PlotStyle
from usecaseclassification.usecaseexecution import UseCaseExecution
from util import configutil
from plot import plotutil


def selector_length_of_use_case_executions_ls(it_unit: Union[UseCaseExecution, BaseExplorationModel],
                                              filtering_entries: Callable,
                                              aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.USE_CASE:
        # it_unit is UseCaseExecution
        return [len(it_unit.get_representative_trace_view().get_transitions())]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


def selector_computed_use_case_executions_number(it_unit: Union[UseCaseExecution, ExplorationModel],
                                                 filtering_entries: Callable,
                                                 aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is ExplorationModel
        return [len(it_unit.use_case_execution_manager.get_computed_use_case_executions())]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


def selector_verified_use_case_executions_number(it_unit: Union[UseCaseExecution, ExplorationModel],
                                                 filtering_entries: Callable,
                                                 aggregation_lvl) -> List[int]:
    if aggregation_lvl == AggregationLevel.APP:
        # it_unit is ExplorationModel
        return [len(it_unit.use_case_execution_manager.get_verified_use_case_executions())]
    else:
        raise NotImplementedError(f"Not implemented yet for: {aggregation_lvl}")


class UseCaseLengthUseCaseExecutions(MultiNumberUCEComparison):
    description = "Length of Use Case Executions"
    name = "Quantity of Edges"
    aggregation_lvls = [AggregationLevel.USE_CASE]
    use_case_whitelist = None
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=UseCaseLengthUseCaseExecutions.aggregation_lvls,
                         data_select_op=selector_length_of_use_case_executions_ls,
                         outlier_method=outlier_method,
                         use_case_whitelist=UseCaseLengthUseCaseExecutions.use_case_whitelist,
                         plot_config=UseCaseLengthUseCaseExecutions.plot_config)


class UseCaseComputedUseCaseExecutionsNumber(MultiNumberUCEComparison):
    description = "Number of computed use case executions"
    name = "Quantity of Computed UCEs"
    aggregation_lvls = [AggregationLevel.APP]
    use_case_whitelist = None
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=UseCaseComputedUseCaseExecutionsNumber.aggregation_lvls,
                         data_select_op=selector_computed_use_case_executions_number,
                         outlier_method=outlier_method,
                         use_case_whitelist=UseCaseComputedUseCaseExecutionsNumber.use_case_whitelist,
                         plot_config=UseCaseComputedUseCaseExecutionsNumber.plot_config)


class UseCaseVerifiedUseCaseExecutionsNumber(MultiNumberUCEComparison):
    description = "Number of verified use case executions"
    name = "Quantity of Verified UCEs"
    aggregation_lvls = [AggregationLevel.APP]
    use_case_whitelist = None
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX)

    def __init__(self,
                 model,
                 outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         aggregation_lvls=UseCaseVerifiedUseCaseExecutionsNumber.aggregation_lvls,
                         data_select_op=selector_verified_use_case_executions_number,
                         outlier_method=outlier_method,
                         use_case_whitelist=UseCaseVerifiedUseCaseExecutionsNumber.use_case_whitelist,
                         plot_config=UseCaseVerifiedUseCaseExecutionsNumber.plot_config)


# TODO change that
PD_FRAME_NAME = "frame"


class UseCaseRatioVerifiedComputedUseCaseExecutionsNumber(BaseSingleEntryMetric):
    description = "Ratio of number of verified/computed use case executions"
    name = "Ratio of Quantity of verified/computed UCEs"

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        data = self.load_data(model)
        super().__init__(UseCaseRatioVerifiedComputedUseCaseExecutionsNumber.name,
                         model,
                         data,
                         AggregationLevel.APP.iter_instance(model=model),
                         outlier_method)

    def compute_data(self, model):
        data = []
        for app in model.apps:
            computed = len(app.exploration_model.use_case_execution_manager.get_computed_use_case_executions())
            if computed == 0:
                d = float(0)
            else:
                verified = len(app.exploration_model.use_case_execution_manager.get_verified_use_case_executions())
                d = float(verified / computed)
            assert d <= 1.0, f"Ratio was: {d}"
            data.append(d)
        return data

    def plot(self):
        yaxis_type = "linear"
        title = f"Metric: {self.get_id()}"
        pd_sorted = self.df.sort_values(by=[PD_FRAME_NAME])

        data = [
            go.Bar(
                x=pd_sorted.index,
                y=[1 for _ in range(len(pd_sorted))],
                marker_color="indianred",
            ),
            go.Bar(
                x=pd_sorted.index,
                y=pd_sorted[PD_FRAME_NAME],
                # name=title,
                marker_color="green",
            )
        ]

        shapes = []
        # Line Horizontal: marker value e.g. mean
        marker_val = self.outlier_method.marker_value()
        marker_line = {
            'type': 'line',
            'x0': -0.5,
            'y0': marker_val,
            'x1': self.nparr.size - 0.5,
            'y1': marker_val,
            'xref': 'x',
            'yref': 'y',
            'line': {
                'color': 'blue',
                'width': 2,
                'dash': configutil.MATRICS_FIGURE_DASH_STYLE,
            },
        }
        shapes.append(marker_line)

        layout = go.Layout(
            # title=self.title(),
            xaxis={
                # 'title': graph_title,
                'automargin': True,
                "tickangle": 50,
            },
            yaxis={
                'automargin': True
            },
            yaxis_type=yaxis_type,
            # margin=dict(l=210, r=25, b=20, t=0, pad=4),
            paper_bgcolor="white",
            plot_bgcolor="white",
            shapes=shapes,
            barmode="overlay",
            showlegend=False,
        )

        html_graph_id = self.get_ui_id()
        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_plot_to_file(data, layout, html_graph_id)
        return dcc.Graph(id=html_graph_id,
                         config=dict(displayModeBar=False),
                         figure=dict(data=data, layout=layout))