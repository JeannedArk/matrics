# -*- coding: utf-8 -*-
from typing import List
import dash_table
from plotly.subplots import make_subplots
import plotly.graph_objs as go

import math

import colorconstants
from aggregationlevel import AggregationLevel
from metrics.datacompound import DataCompound
from metrics.metric import *
from modelaccessor import ModelAccessor
from util import util
from util.latexutil import texify
from util.uiutil import header_metric


ANALYSIS_DISTRIBUTION_HISTOGRAM_CHART_GRAPH_ID = "analysis-distribution-histogram-chart-graph"


class Distribution(ModelAccessor):
    description = "Distribution Analysis"

    def __init__(self, model, outlier_method=None):
        """
        :param outlier_method: We only need it for the call convention.
        """
        super().__init__(model)

    def get_data_compounds(self):
        return []

    def plot(self) -> List[dcc.Graph]:
        apps = self.model.apps
        data_compounds = [
            dc
            for dc in self.model.get_all_data_compounds_with_sane_data()
            if dc.get_aggregation_level() == AggregationLevel.APP
        ]

        self.print_latex_table(data_compounds)

        html_elements = []
        html_elements.append(header_metric("Distribution Table"))

        dt = dash_table.DataTable(
            data=self.get_table_data(data_compounds),
            columns=self.get_columns(),
            style_cell={
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': colorconstants.RGB_COLOR_LIGHT_GREY,
            },
            merge_duplicate_headers=True,
            # style_data_conditional=style_data_conditional,
        )
        html_elements.append(dt)

        html_elements.append(header_metric("Histogram Plots"))
        histogram_plots = self.get_histogram_plots(data_compounds)
        html_elements.append(histogram_plots)

        return html_elements

    def get_columns(self):
        return [
            {"name": f"Metrics", "id": f"metrics"},
            {"name": "Shapiro Wilk p-Value", "id": "shapirowilk"},
            {"name": "Data", "id": "data"},
        ]

    def get_table_data(self, data_compounds: List[DataCompound]):
        df = pd.DataFrame(
            data={
                "metrics": [f"{dc.get_short_id()}_{dc.get_aggregation_level().str_short()}" for dc in data_compounds],
                "data": [str([util.shorten_fl(d) for d in dc.get_data()]) for dc in data_compounds],
                "shapirowilk": [statisticsutil.get_shapiro_p_value(dc.get_data()) for dc in data_compounds],
            }
        )

        return df.to_dict('records')

    def get_histogram_plots(self, data_compounds: List[DataCompound]):
        columns = 4
        width = 1000
        height = 1000

        m = len(data_compounds)
        # assert m == 20, f"Size of metrics: {m}"
        rows = math.ceil(m / columns)
        fig = make_subplots(
            rows=rows,
            cols=columns,
            shared_yaxes=True,
            # shared_xaxes=True,
            # vertical_spacing=0.02,
            subplot_titles=[dc.get_short_id() for dc in data_compounds],
        )

        fig.update_layout(
            # title="Distribution of apps among verified use case executions",
            xaxis={
                'automargin': True,
                # "title": "Title",
                # "tickangle": 50,
            },
            yaxis={
                'automargin': True,
                # "dtick": 5,
                'tickvals': [0, 5, 10, 15, 20]
            },
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            width=width,
            height=height,
            font=dict(
                size=configutil.MATRICS_FIGURE_FONT_SIZE,
                family=configutil.MATRICS_FIGURE_FONT_FAMILY,
            ),
            bargap=0.2,  # gap between bars of adjacent location coordinates
        )

        for i in range(m):
            dc = data_compounds[i]
            histogram = go.Histogram(x=dc.get_data(), name=dc.get_short_id())
            # histogram = go.Histogram(x=[d for d in metric.data])

            r = int(i / columns)
            c = i % columns
            fig.add_trace(histogram, row=r + 1, col=c + 1)

        # https://github.com/plotly/plotly.py/issues/985
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=configutil.MATRICS_FIGURE_FONT_SIZE, family=configutil.MATRICS_FIGURE_FONT_FAMILY)

        graph = dcc.Graph(id=ANALYSIS_DISTRIBUTION_HISTOGRAM_CHART_GRAPH_ID, figure=fig)

        if configutil.MATRICS_FIGURE_DUMP_PLOTS:
            plotutil.write_fig_to_file(fig=fig,
                                       html_graph_id=ANALYSIS_DISTRIBUTION_HISTOGRAM_CHART_GRAPH_ID,
                                       width=width,
                                       height=height)

        return graph

    def print_latex_table(self, data_compounds: List[DataCompound]):
        print(f">>>>>>>>>>>>>> Data distribution table")
        for dc in data_compounds:
            name = texify(dc.get_id())
            print(f"{name} & ${self.get_shapiro_p_value(dc.get_data())}$ \\\\")
