# -*- coding: utf-8 -*-
import os
from typing import List

from plot.boxplotter import BoxPlotlyPlotter, BoxMatplotPlotter, BoxSeabornPlotter
from plotconfiguration import PlotConfiguration, PlotStyle
from util import configutil


SRC_DIR = os.path.abspath(os.path.join("../", configutil.MATRICS_DUMP_VALUE_DIR_NAME))
TARGET_DIR = os.path.abspath(os.path.join("../", configutil.MATRICS_FIGURE_IMAGE_DIR_NAME))
TARGET_FILE = os.path.join(TARGET_DIR, "example.png")
# box_plotter = BoxPlotlyPlotter()
box_plotter = BoxMatplotPlotter()
# box_plotter = BoxSeabornPlotter()
plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                axis_type="log",
                                boxpoints='outliers')


def plot_as_box_plot(json_f: str):
    box_plotter.plot(json_f, TARGET_FILE, plot_config=plot_config)


def plot_as_box_plots(json_fs: List[str]):
    box_plotter.plots("Example plot", json_fs, TARGET_FILE, plot_config=plot_config)


def plot(src_dir):
    for f_name in os.listdir(src_dir)[:100]:
        json_f = os.path.join(src_dir, f_name)
        if os.path.isfile(json_f) and f_name.endswith(".json") and "networkpayloadsizeresponselog" in f_name:
            plot_as_box_plot(json_f)


def plots(src_dir):
    fs = []
    for f_name in os.listdir(src_dir)[:100]:
        json_f = os.path.join(src_dir, f_name)
        if os.path.isfile(json_f) and f_name.endswith(".json") and "networkpayloadsizeresponselog" in f_name:
            fs.append(json_f)

    plot_as_box_plots(fs)


if __name__ == '__main__':
    # json_f = os.path.join(SRC_DIR, "metrics-ucecomparison-networkmetrics-networkpayloadsizerequestuce.json")
    json_f = os.path.join(SRC_DIR, "metrics-ucecomparison-networkmetrics-networkpayloadsizeresponseuce.json")
    # json_f = os.path.join(SRC_DIR, "metrics-ucecomparison-networkmetrics-networklatencyapp.json")
    # plots(SRC_DIR)
    plot_as_box_plot(json_f)
    print(f"\n\n\n++++++++++++++++++++++++ FINISHED ++++++++++++++++++++++++")
