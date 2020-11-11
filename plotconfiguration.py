# -*- coding: utf-8 -*-
import json
from enum import Enum

from jsonexportable import JsonExportable


class PlotStyle(Enum):
    BAR = "bar"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"


class PlotConfiguration(JsonExportable):
    """
    If tickvals are not None, axis_type is ignored.
    """
    def __init__(self,
                 univariate_plot_style: PlotStyle,
                 axis_type=None,
                 tickvals=None,
                 boxpoints='outliers',  # Can be False, 'all', 'outliers', or 'suspectedoutliers'
                 ):
        self.univariate_plot_style = univariate_plot_style
        self.axis_type = axis_type
        self.tickvals = None if tickvals is None else tickvals
        self.boxpoints = boxpoints

    def __repr__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        d = {
            'univariate_plot_style': self.univariate_plot_style.name,
            'axis_type': self.axis_type,
            'tickvals': self.tickvals,
            'boxpoints': self.boxpoints,
        }
        return json.dumps(d, indent=4, sort_keys=True)


class PlotConfigurationDump(object):
    def __init__(self,
                 univariate_plot_style,
                 axis_type,
                 tickvals,
                 boxpoints):
        self.univariate_plot_style = univariate_plot_style
        self.axis_type = axis_type
        self.tickvals = tickvals
        self.boxpoints = boxpoints

    @staticmethod
    def construct(plot_config: PlotConfiguration):
        return PlotConfigurationDump(univariate_plot_style=str(plot_config.univariate_plot_style),
                                     axis_type=plot_config.axis_type,
                                     tickvals=plot_config.axis_type,
                                     boxpoints=plot_config.boxpoints)

    @staticmethod
    def construct_from_json(json_dict):
        return PlotConfigurationDump(univariate_plot_style=json_dict['univariate_plot_style'],
                                     axis_type=json_dict['axis_type'],
                                     tickvals=json_dict['tickvals'],
                                     boxpoints=json_dict['boxpoints'])
