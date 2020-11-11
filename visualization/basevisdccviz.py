# -*- coding: utf-8 -*-
import dash_html_components as html

import colorconstants
from util.configutil import IMG_PATH_DEFAULT
from util.pathutil import get_state_img
from visualization.basemodelviz import BaseModelViz
from visualization.transitionsset import TransitionsSet


class BaseVisdccViz(BaseModelViz):
    """
    Visdcc is an adoption of the original vis.js framework.
    vis.js: https://github.com/visjs/vis-network
    Visdcc: https://github.com/jimmybow/visdcc
    Documentation for networks: https://visjs.github.io/vis-network/docs/network/
    """
    CSS_TOOLTIP_CLASS = "vis-tooltip"

    NODES_PREFIXES_TO_HIGHLIGHT = []

    @staticmethod
    def get_options(heigth="600px", hierarchical_layout=False):
        options = dict(
            autoResize=True,
            height=heigth,
            width='100%',
            locale='en',
            layout=dict(
                hierarchical=dict(
                    enabled=hierarchical_layout,
                    direction='LR'
                ),
                improvedLayout=False,
            ),
            nodes=dict(
                shape='image',
                brokenImage=IMG_PATH_DEFAULT,
                shapeProperties=dict(useBorderWithImage=True),
                borderWidth=2,
                borderWidthSelected=5,
                color=dict(
                    border=colorconstants.HEX_COLOR_WHITE,
                    background=colorconstants.HEX_COLOR_WHITE,
                    highlight=dict(border=colorconstants.HEX_COLOR_BLUE, background=colorconstants.HEX_COLOR_BLUE)
                ),
                font=dict(size=12, color='#000')
            ),
            edges=dict(
                color=dict(
                    color=colorconstants.STR_COLOR_BLACK,
                    highlight=colorconstants.HEX_COLOR_BLUE,
                ),
                length=200,
                arrows=dict(
                    to=dict(enabled=True, scaleFactor=1.0)
                ),
                font=dict(size=12, color='#000'),
                width=2,
            ),
            interaction=dict(hover=True, tooltipDelay=30),
            # physics=False,
            physics=dict(stabilization=dict(
                iterations=200
            ))
        )
        return options

    def transform_state(self, state, shortened_state_len=15, internal_state_id=None, color=None, is_app_home_state=False):
        id = state.unique_id if internal_state_id is None else internal_state_id
        # atd_records_str = [atd_rec.tooltip_info() for atd_rec in state.atd_records]
        atd_records_str = "\n".join([atd_rec.tooltip_info() for atd_rec in state.atd_records])
        img_small_path = None if not state.image_small_paths else next(iter(state.image_small_paths))
        s = {
            'id': f"{id}",
            'label': f"{state.shortened_state_id(length=shortened_state_len)}",
            'image': {
                'selected': get_state_img(img_small_path),
                'unselected': get_state_img(img_small_path),
            },
            'title': f""
            f"<p class='{BaseVisdccViz.CSS_TOOLTIP_CLASS}'><b>Node</b>: {state.unique_id}</p>"
            # f"<p class='{BaseVisdccViz.CSS_TOOLTIP_CLASS}'><b>Features (pruned)</b>: {sorted(state.unique_features)}</p>"
            # f"<p class='{BaseVisdccViz.CSS_TOOLTIP_CLASS}'><b>ATDRecords</b>: {atd_records_str}</p>"
            # f"<p class='{BaseVisdccViz.CSS_TOOLTIP_CLASS}'><b>Use case names</b>: {[uc.name for uc in state.use_cases]}</p>"
            # f"<p class='{BaseVisdccViz.CSS_TOOLTIP_CLASS}'><b>Use cases (exhausting)</b>: {[uc.to_string_short() for uc in state.use_cases]}</p>"
        }
        if color is not None:
            s['color'] = color
        if is_app_home_state:
            print(f"Highlight app home state: {state}")
            s['borderWidth'] = 3
            s['color'] = dict(
                border=colorconstants.HEX_COLOR_GREEN,
                background=colorconstants.HEX_COLOR_GREEN,
                highlight=dict(border=colorconstants.HEX_COLOR_GREEN, background=colorconstants.HEX_COLOR_GREEN)
            )
        if any(state.unique_id.startswith(highlight_id) for highlight_id in BaseVisdccViz.NODES_PREFIXES_TO_HIGHLIGHT):
            print(f"Highlight: {state}")
            s['borderWidth'] = 3
            s['color'] = dict(
                border=colorconstants.HEX_COLOR_RED,
                background=colorconstants.HEX_COLOR_RED,
                highlight=dict(border=colorconstants.HEX_COLOR_RED, background=colorconstants.HEX_COLOR_RED)
            )

        return s

    def transform_edge(self, trans):
        id_e = f"{trans.source_state_o.unique_id} -> {trans.resulting_state_o.unique_id}"
        edge = {
            'id': id_e,
            'from': f"{trans.source_state_o.unique_id}",
            'to': f"{trans.resulting_state_o.unique_id}",
            'label': None,  # Will be set in process_edges in a postprocessing step
            'transitionsset': TransitionsSet(trans),
        }

        if any(trans.source_state_o.unique_id.startswith(highlight_id) for highlight_id in BaseVisdccViz.NODES_PREFIXES_TO_HIGHLIGHT)\
                or any(trans.resulting_state_o.unique_id.startswith(highlight_id) for highlight_id in BaseVisdccViz.NODES_PREFIXES_TO_HIGHLIGHT):
            edge['color'] = dict(color=colorconstants.HEX_COLOR_RED)
            edge['width'] = 5

        return id_e, edge

    def process_edges(self, transitions):
        edges = []
        # edge id -> (index in self.edges, list of corresponding original transitions)
        id_edge_map = {}
        idx = 0
        for trans in transitions:
            id_e, edge = self.transform_edge(trans)
            if id_e in id_edge_map:
                idx_, _ = id_edge_map[id_e]
                (edges[idx_])['transitionsset'].add(trans)
                id_edge_map[id_e][1].append(trans)
            else:
                edges.append(edge)
                id_edge_map[id_e] = (idx, [trans])
                idx += 1

        for edge in edges:
            edge['label'] = str(edge['transitionsset'])

        return edges, id_edge_map

    def node_info(self, state):
        # [html.P(atd_rec.graph_info()) for atd_rec in self.model.uid_state_map[n_uid].atd_records] +\
        # TODO for presentation purposes use image_atd_paths
        ui_elem = [html.P(f"Node: {state.unique_id}")] + \
        [
            html.Img(id=f"node_img_{state.unique_id}", src=get_state_img(image_path), style={'width': '600px'})
            for image_path in state.image_paths
        ]   +\
        [html.P(f"Merged states:")] +\
        [
            html.Pre(f"{merged_state}") for merged_state in state.merged_states
        ] +\
        [html.P(f"ATDs:")] +\
        [html.P(atd_rec.graph_info()) for atd_rec in state.atd_records] +\
        [
            html.P(f"Features (pruned): {state.unique_features}"),
            html.P(f"Features: {state.features}"),
            html.P(f"Use cases: {[uc.to_string_short() for uc in state.use_cases]}"),
        ]
        return ui_elem

    def edges_info(self, edges):
        ui_elem = []
        for e in edges:
            # Example: e = 65433237-52b58d7e46a6_939f1c74... -> 680ebd47-a04e-...
            ui_elem.append(html.P(f"Edge: {e}"))
            _, transitions = self.id_edge_map[e]
            for t in transitions:
                ui_elem.append(html.Pre(f"{t.graph_info()}"))
        return ui_elem
