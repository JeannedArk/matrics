# -*- coding: utf-8 -*-
import statistics

import dash_bootstrap_components as dbc
from typing import List, Dict, Callable

from aggregationlevel import AggregationLevel
from metrics.datacompound import DataCompound
from metrics.metric import *
from metrics.ucecomparison import playstoremetrics
from metrics.ucecomparison.usecasemetrics import UseCaseComputedUseCaseExecutionsNumber
from model.usecase import UseCase
from modelaccessor import ModelAccessor
from util.modelutil import calculate_use_case_matrix
from util.uiutil import header_metric


USE_CASE_STATE_COMPUTED = "COMPUTED"
USE_CASE_STATE_VERIFIED = "VERIFIED"
USE_CASE_STATE_DEFINED_FOR_APP = "DEFINED"
USE_CASE_EXECUTIONS_CORRELATION_HEATMAP_GRAPH_ID = "use-case-executions-correlation-heatmap-graph"


class CorrelationsMetricAppAL(ModelAccessor):
    description = "Metrics Correlation on App Aggregation Level"

    aggregation_functions = [
        (statistics.median, "median"),
        (np.mean, "mean"),
    ]
    methods = [
        'pearson',  # Gaussian or Gaussian-like distribution
        'spearman',
        'kendall',
    ]
    filtered_metrics = [
        playstoremetrics.PlayStoreInstallationNumber.name,
        playstoremetrics.PlayStoreReviewNumber.name,
        playstoremetrics.PlayStoreRating.name,
        UseCaseComputedUseCaseExecutionsNumber.name,
    ]
    height = 1000
    width = 1200

    def __init__(self, model, outlier_method=None):
        """
        :param outlier_method: We only need it for the call convention.
        """
        super().__init__(model)

    def get_data_compounds(self):
        return []

    def aggregate_data(self, aggr_func: Callable, d: Dict) -> List:
        return [aggr_func(v) if len(v) else np.NAN
                for _, v in d.items()]

    def plot(self) -> List[dcc.Graph]:
        html_elements = []
        apps = self.model.apps
        data_compounds: List[DataCompound] = [
            dc
            for dc in self.model.get_all_data_compounds_with_sane_data()
            if dc.get_aggregation_level() == AggregationLevel.APP and dc.name not in CorrelationsMetricAppAL.filtered_metrics
        ]

        for aggr_func, aggr_func_name in CorrelationsMetricAppAL.aggregation_functions:
            # All valid metrics data for a correlation analysis
            metrics_data = {
                f"{dc.name}": self.aggregate_data(aggr_func, dc.data)
                for dc in data_compounds
                if len(self.aggregate_data(aggr_func, dc.data)) == len(apps)
            }
            assert len(metrics_data), f"Metrics data was empty"

            metrics_df = pd.DataFrame(metrics_data)
            for method in CorrelationsMetricAppAL.methods:
                title = f'Correlation Matrix ({method}) ({aggr_func_name})'
                html_elements.append(header_metric(title))
                corr = statisticsutil.calc_correlation_matrix(metrics_df, method)
                heat, layout = plotutil.get_correlations_heatmap(corr)

                graph = dcc.Graph(id=f"correlation-graph-{method}-{aggr_func_name}",
                                  style={
                                      'height': f'{CorrelationsMetricAppAL.height}px',
                                      'width': f'{CorrelationsMetricAppAL.width}px',
                                  },
                                  config=dict(displayModeBar=False),
                                  figure=dict(data=[heat], layout=layout))

                if configutil.MATRICS_FIGURE_DUMP_PLOTS:
                    plotutil.write_plot_to_file([heat],
                                                layout,
                                                f"{CorrelationsMetricAppAL.get_id()}-{method}-{aggr_func_name}",
                                                width=CorrelationsMetricAppAL.width,
                                                height=CorrelationsMetricAppAL.height)

                html_elements.append(graph)

        return html_elements


class UseCaseCorrelations(ModelAccessor, BaseDataCache):
    description = "Use Case Correlations"

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model)

    def get_cache_load_id(self) -> str:
        return self.get_id()

    def get_data_compounds(self):
        return []

    def compute_data(self, apps):
        return calculate_use_case_matrix(apps, self.model)

    def calculate_number_of_atds(self, use_cases: List[UseCase]):
        return [len(use_case.atds_flatted) for use_case in use_cases]

    def calculate_number_of_words(self, use_cases: List[UseCase]):
        return [sum(len(atd.target_descriptor.split()) for atd in use_case.atds_flatted) for use_case in use_cases]

    def calculate_number_of_computed_use_case_executions(self, apps, matrix, use_cases: List[UseCase]):
        return [sum(1 for app in apps if matrix[app.package_name][use_case.name][USE_CASE_STATE_COMPUTED])
                for use_case in use_cases]

    def calculate_number_of_verified_use_case_executions(self, apps, matrix, use_cases: List[UseCase]):
        return [sum(1 for app in apps if matrix[app.package_name][use_case.name][USE_CASE_STATE_VERIFIED])
                for use_case in use_cases]

    def plot(self):
        html_elements = []
        correlation_graph = self.get_correlation_graph()
        html_elements.extend(correlation_graph)

        return dbc.Container(id=self.get_ui_id(), children=html_elements)

    def get_correlation_graph(self):
        apps = sorted(self.model.apps)
        matrix = self.load_data(apps)
        use_cases_all = self.model.use_case_manager.get_use_cases()
        number_of_atds = self.calculate_number_of_atds(use_cases_all)
        number_of_words = self.calculate_number_of_words(use_cases_all)
        number_of_verified_uce = self.calculate_number_of_verified_use_case_executions(apps, matrix, use_cases_all)
        number_of_computed_uce = self.calculate_number_of_computed_use_case_executions(apps, matrix, use_cases_all)

        df = pd.DataFrame({
            "Number of ATDs": number_of_atds,
            "Number of words in use case": number_of_words,
            "Number of computed UCEs": number_of_computed_uce,
            "Number of verified UCEs": number_of_verified_uce,
        })

        # method = "pearson"
        methods = [
            'pearson',  # Gaussian or Gaussian-like distribution
            'spearman',
            'kendall',
        ]
        height = 500
        width = 600

        html_elements = []
        for method in methods:
            title = f'Correlation Matrix ({method})'
            html_elements.append(header_metric(title))
            corr = statisticsutil.calc_correlation_matrix(df, method)
            heat, layout = plotutil.get_correlations_heatmap(corr)

            graph = dcc.Graph(id=f"correlation-graph-{method}",
                              style={
                                  'height': f'{height}px',
                                  'width': f'{width}px',
                              },
                              config=dict(displayModeBar=False),
                              figure=dict(data=[heat], layout=layout))

            if configutil.MATRICS_FIGURE_DUMP_PLOTS:
                plotutil.write_plot_to_file([heat],
                                            layout,
                                            f"{USE_CASE_EXECUTIONS_CORRELATION_HEATMAP_GRAPH_ID}-{method}",
                                            width=width,
                                            height=height)

            html_elements.append(graph)

        return html_elements
