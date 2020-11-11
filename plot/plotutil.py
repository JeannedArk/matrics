# -*- coding: utf-8 -*-
from typing import List, Tuple

import plotly.graph_objs as go
import dash_core_components as dcc
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

import colorconstants
from plotconfiguration import PlotStyle, PlotConfiguration
from util import pathutil, configutil
from util.configutil import MATRICS_FIGURE_DEFAULT_HEIGHT, MATRICS_FIGURE_VERTICAL_HEIGHT_PER_ENTRY, \
    MATRICS_FIGURE_DEFAULT_PADDING


def select_color(is_outlier: bool):
    return colorconstants.RGBA_COLOR_RED if is_outlier else colorconstants.RGBA_COLOR_GREY


def select_colors(outlier_method, df):
    return [select_color(outlier_method.is_outlier(v)) for v in df]


def get_height_for_vertical_extendable_plots(entries, plot_style: PlotStyle):
    if plot_style == PlotStyle.BAR:
        height = 25 * entries if entries > 0 else MATRICS_FIGURE_DEFAULT_HEIGHT
    elif plot_style == PlotStyle.BOX or plot_style == PlotStyle.VIOLIN:
        height = MATRICS_FIGURE_VERTICAL_HEIGHT_PER_ENTRY * entries if entries > 0 else MATRICS_FIGURE_DEFAULT_HEIGHT
    else:
        raise NotImplementedError(f"Unknown plot style: {plot_style}")
    res = height + MATRICS_FIGURE_DEFAULT_PADDING
    return res


def get_height_for_vertical_extendable_plots_writing(entries: int, plot_style: PlotStyle):
    """
    Need different settings when dumping the plot in an image.
    """
    if plot_style == PlotStyle.BOX or plot_style == PlotStyle.VIOLIN:
        height = 30 * entries if entries > 0 else MATRICS_FIGURE_DEFAULT_HEIGHT
    else:
        raise NotImplementedError(f"Unknown plot style: {plot_style}")
    # Punish single entries
    if entries == 1:
        bonus = 30
    else:
        bonus = 80
    res = height + bonus
    return res


def get_bar_plot(indices,
                 outlier_method,
                 values,
                 layout_title,
                 bar_title,
                 yaxis_type):

    data = [go.Bar(
        x=indices,
        y=values,
        name=bar_title,
        marker=dict(
            color=select_colors(outlier_method, values)
        ),
    )]
    shapes = []
    # Line Horizontal: marker value e.g. mean
    marker_val = outlier_method.marker_value()
    marker_line = {
        'type': 'line',
        'x0': -0.5,
        'y0': marker_val,
        'x1': len(values) - 0.5,
        'y1': marker_val,
        'xref': 'x',
        'yref': 'y',
        'line': {
            'color': 'blue',
            'width': configutil.MATRICS_FIGURE_LINE_WIDTH,
            'dash': configutil.MATRICS_FIGURE_DASH_STYLE,
        },
    }
    shapes.append(marker_line)
    if outlier_method.has_lower_bound():
        lower = outlier_method.lower_bound()
        # Line Horizontal: Lower cutoff
        lb = {
            'type': 'line',
            'x0': -0.5,
            'y0': lower,
            'x1': len(values) - 0.5,
            'y1': lower,
            'xref': 'x',
            'yref': 'y',
            'line': {
                'color': 'red',
                'width': configutil.MATRICS_FIGURE_LINE_WIDTH,
                'dash': configutil.MATRICS_FIGURE_DASH_STYLE,
            },
        }
        shapes.append(lb)
    if True:
        upper = outlier_method.upper_bound()
        # Line Horizontal: Upper cutoff
        ub = {
            'type': 'line',
            'x0': -0.5,
            'y0': upper,
            'x1': len(values) - 0.5,
            'y1': upper,
            'xref': 'x',
            'yref': 'y',
            'line': {
                'color': 'red',
                'width': configutil.MATRICS_FIGURE_LINE_WIDTH,
                'dash': configutil.MATRICS_FIGURE_DASH_STYLE,
            },
        }
        shapes.append(ub)

    layout = go.Layout(
        title=layout_title,
        xaxis=dict(
            # 'title': graph_title,
            automargin=True,
        ),
        yaxis=dict(
            automargin=True,
        ),
        yaxis_type=yaxis_type,
        # margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        shapes=shapes,
    )

    return data, layout


def get_box_plot(values,
                 indices,
                 layout_title: str,
                 box_title: str,
                 axis_type: str,  # TODO
                 ):

    data = [go.Box(
        y=values,
        name=box_title,
        boxpoints='all',
        # boxpoints='suspectedoutliers',
        text=indices,
        # customdata=sorted.index,
        customdata=indices,
        hoverinfo="text+y",
        marker=dict(
            outliercolor=colorconstants.RGB_COLOR_RED,
            line=dict(
                outliercolor=colorconstants.RGB_COLOR_RED,
                outlierwidth=2
            ),
        ),
    )]

    layout = go.Layout(
        title=layout_title,
        xaxis=dict(
            # 'title': graph_title,
            automargin=True,
        ),
        yaxis=dict(
            automargin=True,
        ),
        # yaxis_type=yaxis_type,
        # margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
    )

    return data, layout


def get_box_subplots(layout_title, data: List[Tuple[str, List[str], List]], axis_type: str):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_yaxes=False,
    )

    if data:
        title, indices, values = data[0]
        box = go.Box(
            x=values,
            # y=values,
            name=title,
            boxpoints='all',
            # boxpoints='suspectedoutliers',
            text=indices,
            # customdata=indices,
            # hoverinfo="text+y",
            hoverinfo="text+x",
            # boxmean='sd',
            marker=dict(
                outliercolor=colorconstants.RGB_COLOR_RED,
                line=dict(
                    outliercolor=colorconstants.RGB_COLOR_RED,
                    outlierwidth=2
                ),
            ),
            orientation='h',
        )
        fig.add_trace(box, row=1, col=1)

    if data:
        for title, indices, values in data[1:]:
            assert len(indices) == len(values), f"Indices: {len(indices)} values: {len(values)}"

            box = go.Box(
                x=values,
                # y=values,
                name=title,
                boxpoints='all',
                # boxpoints='suspectedoutliers',
                text=indices,
                # customdata=indices,
                # hoverinfo="text+y",
                hoverinfo="text+x",
                # boxmean='sd',
                marker=dict(
                    outliercolor=colorconstants.RGB_COLOR_RED,
                    line=dict(
                        outliercolor=colorconstants.RGB_COLOR_RED,
                        outlierwidth=2
                    ),
                ),
                orientation='h',
            )
            fig.add_trace(box, row=2, col=1)

    height = get_height_for_vertical_extendable_plots(len(data), PlotStyle.BOX)
    layout = go.Layout(
        height=height,
        title=layout_title,
        xaxis=dict(
            automargin=True,
            # tickmode="array",
            type=axis_type,
            # tick0=0.0001,
            # tickvals=arr,
            # ticktext=arr,
        ),
        yaxis=dict(
            automargin=True,
        ),
        # yaxis_type=yaxis_type,
        # margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
        legend=dict(traceorder='normal'),
    )

    fig.update_layout(layout)
    graph = dcc.Graph(figure=fig)

    return graph


def get_box_plots_config(layout_title, data: List[Tuple[str, List[str], List]], plot_config: PlotConfiguration):
    boxes = []
    for title, indices, values in data:
        assert len(indices) == len(values), f"Indices: {len(indices)} values: {len(values)}"

        box = go.Box(
            x=values,
            # y=values,
            name=title,
            boxpoints=plot_config.boxpoints,
            text=indices,
            # customdata=indices,
            # hoverinfo="text+y",
            hoverinfo="text+x",
            # boxmean='sd',
            whiskerwidth=0,
            width=0.9,
            marker=dict(
                outliercolor=colorconstants.RGB_COLOR_RED,
                line=dict(
                    outliercolor=colorconstants.RGB_COLOR_RED,
                    outlierwidth=2
                ),
            ),
            orientation='h',
        )
        boxes.append(box)

    height = get_height_for_vertical_extendable_plots(len(data), PlotStyle.BOX)
    layout_xaxis=dict(
        automargin=True,
        zeroline=False,
        rangemode="tozero",  # Can also be normal (default) and nonnegative, but tozero draws the 0 in a non log scale
    )
    if plot_config.tickvals:
        # tick0=0.0001,
        # ticktext=[str(t) for t in plot_config.tickvals],
        layout_xaxis["tickmode"] = "array"
        layout_xaxis["tickvals"] = plot_config.tickvals
    else:
        layout_xaxis["type"] = plot_config.axis_type

    boxgap = 0.8 if len(boxes) == 1 else 0.3
    layout = go.Layout(
        height=height,
        width=1077.5,
        title=layout_title,
        xaxis=layout_xaxis,
        yaxis=dict(
            automargin=True,
        ),
        # margin=dict(l=250, r=50, b=5, t=0, pad=5),
        # margin=dict(l=250, r=50, pad=5),
        margin=dict(pad=5),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
        showlegend=False,
        # Group does not work very well
        # boxmode='group',
        boxgap=boxgap,
        # boxgroupgap=0,
    )

    return boxes, layout


def get_box_plots(layout_title, data: List[Tuple[str, List[str], List]], axis_type: str):
    boxes = []
    for title, indices, values in data:
        assert len(indices) == len(values), f"Indices: {len(indices)} values: {len(values)}"

        box = go.Box(
            x=values,
            # y=values,
            name=title,
            boxpoints='all',
            # boxpoints='suspectedoutliers',
            text=indices,
            # customdata=indices,
            # hoverinfo="text+y",
            hoverinfo="text+x",
            # boxmean='sd',
            marker=dict(
                outliercolor=colorconstants.RGB_COLOR_RED,
                line=dict(
                    outliercolor=colorconstants.RGB_COLOR_RED,
                    outlierwidth=2
                ),
            ),
            orientation='h',
        )
        boxes.append(box)

    height = get_height_for_vertical_extendable_plots(len(data), PlotStyle.BOX)
    layout = go.Layout(
        height=height,
        title=layout_title,
        xaxis=dict(
            automargin=True,
            # tickmode="array",
            type=axis_type,
            # tick0=0.0001,
            # tickvals=arr,
            # ticktext=arr,
        ),
        yaxis=dict(
            automargin=True,
        ),
        # yaxis_type=yaxis_type,
        # margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
        # Group does not work very well
        # boxmode='group',
        # boxgap=0.25,
        # boxgroupgap=0,
    )

    return boxes, layout


def get_violin_plots(layout_title, data: List[Tuple[str, List[str], List]]):
    """
    Plotly documentation: https://plotly.com/python/violin/
    """
    violins = []
    for title, indices, values in data:
        assert len(indices) == len(values), f"Indices: {len(indices)} values: {len(values)}"

        violin = go.Violin(
            x=values,
            # y=values,
            text=indices,
            name=title,
            points="all",
            box_visible=True,
            hoverinfo="text+x",
        )
        violins.append(violin)

    height = get_height_for_vertical_extendable_plots(len(data), PlotStyle.VIOLIN)
    layout = go.Layout(
        height=height,
        title=layout_title,
        xaxis=dict(
            automargin=True,
        ),
        yaxis=dict(
            automargin=True,
        ),
        # yaxis_type=yaxis_type,
        # margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
        # violinmode='group',
        # violingap=0,
    )

    return violins, layout


def get_correlations_heatmap(corr: pd.DataFrame, triangle=True):
    corrz = None
    labels_x = None
    labels_y = None
    if triangle:
        # Generate a mask for the upper triangle
        mask = np.zeros_like(corr, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        corrz = corr.mask(mask)
        labels = corrz.columns.values

        corrz = corrz.drop(corrz.columns[[len(labels) - 1]], axis=1)
        corrz.drop(corrz.index[[0]], inplace=True)
        labels_x = labels[:-1]
        labels_y = labels[1:]
    else:
        labels_x = corr.columns.values[:-1]
        labels_y = corr.index.values
        corrz = corr

    heat = go.Heatmap(
        z=corrz,
        x=labels_x,
        y=labels_y,
        xgap=5,
        ygap=5,
        colorbar=dict(
            title="Correlation Coefficient",
            # tick0=-1.0,
            dtick=0.2,
            tickmode='array',
            tickvals=[-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        ),
        zmin=-1.0,
        zmax=1.0,
        colorscale='RdBu',
    )

    layout = go.Layout(
        # title_text=title,
        autosize=True,
        xaxis=dict(
            automargin=True,
            tickangle=-50,
            showgrid=False,
        ),
        yaxis=dict(
            automargin=True,
            showgrid=False,
            autorange='reversed',
        ),
        plot_bgcolor=colorconstants.HEX_COLOR_WHITE,
        font=dict(
            size=configutil.MATRICS_FIGURE_FONT_SIZE,
            # family=configutil.MATRICS_FIGURE_FONT_FAMILY,
        ),
    )

    return heat, layout


def write_plot_to_file(data, layout, html_graph_id, width=1050, height=None, plot_style=PlotStyle.BOX):
    # tmp_title = layout.title
    # tmp_margin = layout.margin
    # layout.title = None
    # layout.margin = dict(l=250, r=50, b=5, t=0, pad=5)
    fig = go.Figure(
        data=data,
        layout=layout,
    )

    if height is None:
        height = 500
        if plot_style == PlotStyle.BOX:
            height = get_height_for_vertical_extendable_plots_writing(len(data), PlotStyle.BOX)
        elif plot_style == PlotStyle.HEATMAP:
            height = 500
    write_fig_to_file(fig=fig, html_graph_id=html_graph_id, width=width, height=height)
    # layout.title = tmp_title
    # layout.margin = tmp_margin


def write_fig_to_file(fig, html_graph_id, width=1050, height=450):
    # https://plotly.github.io/plotly.py-docs/generated/plotly.io.write_image.html
    fig.write_image(pathutil.get_figure_image_path(html_graph_id), width=width, height=height, scale=2)
