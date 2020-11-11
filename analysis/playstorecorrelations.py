# -*- coding: utf-8 -*-
import statistics

from typing import List, Dict, Callable

from aggregationlevel import AggregationLevel
from metrics.datacompound import DataCompound
from metrics.metric import *
from metrics.ucecomparison import playstoremetrics
from metrics.ucecomparison.usecasemetrics import UseCaseComputedUseCaseExecutionsNumber
from modelaccessor import ModelAccessor
from util.uiutil import header_metric


white_list = [
    playstoremetrics.PlayStoreRating.name,
    playstoremetrics.PlayStoreReviewNumber.name,
    playstoremetrics.PlayStoreInstallationNumber.name
]


class PlayStoreCorrelationsMetricAppAL(ModelAccessor):
    description = "Play Store Metrics Correlation on App Aggregation Level"

    aggregation_functions = [
        (statistics.median, "median"),
        # (np.mean, "mean"),
    ]
    methods = [
        'pearson',  # Gaussian or Gaussian-like distribution
        'spearman',
        'kendall',
    ]
    filtered_metrics = [
        UseCaseComputedUseCaseExecutionsNumber.name,
    ]
    height = 460
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
            if dc.get_aggregation_level() == AggregationLevel.APP and dc.name not in PlayStoreCorrelationsMetricAppAL.filtered_metrics
        ]

        for aggr_func, aggr_func_name in PlayStoreCorrelationsMetricAppAL.aggregation_functions:
            # All valid metrics data for a correlation analysis
            metrics_data = {
                f"{dc.name}": self.aggregate_data(aggr_func, dc.data)
                for dc in data_compounds
                if len(self.aggregate_data(aggr_func, dc.data)) == len(apps)
            }
            assert len(metrics_data), f"Metrics data was empty"

            metrics_df = pd.DataFrame(metrics_data)
            for method in PlayStoreCorrelationsMetricAppAL.methods:
                title = f'Correlation Matrix ({method}) ({aggr_func_name})'
                html_elements.append(header_metric(title))
                corr = statisticsutil.calc_correlation_matrix(metrics_df, method, white_list)
                heat, layout = plotutil.get_correlations_heatmap(corr, triangle=False)

                graph = dcc.Graph(id=f"play-store-correlation-graph-{method}-{aggr_func_name}",
                                  style={
                                      'height': f'{PlayStoreCorrelationsMetricAppAL.height}px',
                                      'width': f'{PlayStoreCorrelationsMetricAppAL.width}px',
                                  },
                                  config=dict(displayModeBar=False),
                                  figure=dict(data=[heat], layout=layout))

                if configutil.MATRICS_FIGURE_DUMP_PLOTS:
                    plotutil.write_plot_to_file([heat],
                                                layout,
                                                f"{PlayStoreCorrelationsMetricAppAL.get_id()}-{method}-{aggr_func_name}",
                                                width=PlayStoreCorrelationsMetricAppAL.width,
                                                height=PlayStoreCorrelationsMetricAppAL.height)

                html_elements.append(graph)

        return html_elements
