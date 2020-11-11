# -*- coding: utf-8 -*-
import traceback
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from metrics.datacompound import DataCompound, DataCompoundDump
from plot import plotutil
from plot.baseplotter import BasePlotter
from plotconfiguration import PlotConfiguration


class BoxPlotlyPlotter(BasePlotter):
    def plot_data_compound(self, title, dc: DataCompoundDump, target_f, plot_config: PlotConfiguration, show=False):
        d = self.get_data_w_labels(dc.data, "Name")
        data, layout = plotutil.get_box_plots(layout_title=dc.id, data=[d], axis_type=plot_config.axis_type)
        plotutil.write_plot_to_file(data, layout, f"{dc.id}-box")

    def plot_data_compounds(self, title, dcs: List[DataCompoundDump], target_f, plot_config: PlotConfiguration, show=False):
        pass


class BoxMatplotPlotter(BasePlotter):
    # flierprops = dict(markerfacecolor='r', marker='s')
    flierprops = dict(markerfacecolor='b', marker='s')

    def plot_data_compound(self, title, dc: DataCompoundDump, target_f, plot_config: PlotConfiguration, show=False):
        fig, ax = plt.subplots()
        fig.set_size_inches(self.get_width(), self.get_height_for_vertical_extendable_plots(1))
        ax.set_title(title)
        ax.boxplot(self.get_data(dc), vert=False, flierprops=BoxMatplotPlotter.flierprops)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        # ax.spines['left'].set_visible(True)
        # ax.set_frame_on(False)
        ax.margins(0)
        ax.set_ylabel(dc.get_chart_title(), rotation=0, fontsize=self.get_font_size(), labelpad=self.get_ylabel_pad())

        if plot_config.axis_type == "log":
            ax.set_xscale('log')
        # if plot_config.tickvals:
        #     ax.set_xticks(plot_config.tickvals)
        #     ax.set_yticklabels(plot_config.tickvals)
        plt.autoscale(True)
        plt.tight_layout()
        plt.savefig(target_f)
        if show:
            plt.show()

    def plot_data_compounds(self, title, dcs: List[DataCompoundDump], target_f, plot_config: PlotConfiguration, show=False):
        if len(dcs) == 1:
            return self.plot_data_compound(title, dcs[0], target_f, plot_config, show)
        try:
            fig, axes = plt.subplots(nrows=len(dcs))
            fig.set_size_inches(self.get_width(), self.get_height_for_vertical_extendable_plots(len(dcs)))
            fig.subplots_adjust(hspace=1.0)
            for ax, dc in zip(axes, dcs):
                ax.boxplot(self.get_data(dc), vert=False, flierprops=BoxMatplotPlotter.flierprops)
                ax.set_yticks([])
                # ax.spines['top'].set_visible(False)
                # ax.spines['right'].set_visible(False)
                # ax.spines['bottom'].set_visible(False)
                # ax.set_frame_on(False)
                ax.margins(0.85)
                ax.set_ylabel(dc.get_chart_title(), rotation=0, fontsize=self.get_font_size(), labelpad=self.get_ylabel_pad())

            print(f"Save fig into {target_f}")
            plt.title(title)
            plt.autoscale(True)
            plt.tight_layout()
            plt.savefig(target_f)
            if show:
                plt.show()
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def get_ylabel_pad(self):
        return 30

    def get_font_size(self):
        return 10

    def get_width(self):
        return 9

    def get_height_for_vertical_extendable_plots(self, entries: int):
        default = 3
        padding = 2
        FIGURE_VERTICAL_HEIGHT_PER_ENTRY = 1
        height = FIGURE_VERTICAL_HEIGHT_PER_ENTRY * entries if entries > 0 else default
        return height + padding


class BoxSeabornPlotter(BasePlotter):
    def plot_data_compound(self, title, dc: DataCompoundDump, target_f, plot_config: PlotConfiguration, show=False):
        pass

    def plot_data_compounds(self, title, dcs: List[DataCompoundDump], target_f, plot_config: PlotConfiguration, show=False):
        data = {
            "Name": pd.Series([dc.id for dc in dcs]),
            "data": pd.Series([self.get_data(dc) for dc in dcs])
        }
        df = pd.DataFrame(data)
        sns.boxplot(y='Name',
                    x='data',
                    orient='h',
                    data=[self.get_data(dc) for dc in dcs],
                    # data=df,
                    # palette="colorblind",
                    # hue='year'
                    )