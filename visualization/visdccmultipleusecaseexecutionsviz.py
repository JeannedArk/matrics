# -*- coding: utf-8 -*-
import collections

import dash_html_components as html
import dash_bootstrap_components as dbc
import visdcc

import colorconstants
import metadata
from graph.path import Path
from metadata import MetaData
from visualization.basevisdccviz import BaseVisdccViz


LIMIT = 2
MULTIPLE_USE_CASE_EXECUTION_GRAPH_HTML_ID = 'vis-multiple-use-case-execution'


class VisdccMultipleUseCaseExecutionsViz(BaseVisdccViz):
    GRAPH_HEIGHT = "300px"
    SHORTENED_STATE_NAME_LEN = 4

    def __init__(self, exploration_model):
        super().__init__(MULTIPLE_USE_CASE_EXECUTION_GRAPH_HTML_ID)
        self.data = collections.defaultdict(list)
        for use_case_exec in exploration_model.use_case_execution_manager.use_case_executions:
            use_case_exec_paths: list = use_case_exec.get_computed_paths_selection()
            # use_case_exec_paths: list = use_case_exec.get_candidates()[:LIMIT]
            for path_cnt, use_case_exec_path in enumerate(use_case_exec_paths):
                uc_exec_trace = use_case_exec_path.trace
                assert uc_exec_trace is not None
                uc_exec_seq = uc_exec_trace.sequence
                _, transitions, _ = uc_exec_seq.get_flatted_representation()
                meta_data_ls: list = uc_exec_trace.meta_data
                assert len(transitions) == len(meta_data_ls), f"Transitions len was {len(transitions)}, meta data len was {meta_data_ls}"
                # transitions = uc_exec_trace.transitions
                state_counter_map = collections.defaultdict(int)
                states = []
                # We don't need process_edges for this case
                edges = []

                last_res_s = None
                for i, trans in enumerate(transitions):
                    meta_data: MetaData = meta_data_ls[i]
                    src_s = trans.source_state_o
                    cnt = state_counter_map[src_s.unique_id]
                    src_state_internal_id = f"{src_s.shortened_state_id(length=VisdccMultipleUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})_{path_cnt}"
                    res_s = trans.resulting_state_o

                    if last_res_s != src_s:
                        state_counter_map[src_s.unique_id] += 1
                        cnt = state_counter_map[src_s.unique_id]
                        src_state_internal_id = f"{src_s.shortened_state_id(length=VisdccMultipleUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})_{path_cnt}"
                        color = None if not meta_data.is_empty() else VisdccMultipleUseCaseExecutionsViz.get_node_color_highlight()
                        states.append(self.transform_state(state=src_s,
                                                           internal_state_id=src_state_internal_id,
                                                           shortened_state_len=VisdccMultipleUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN,
                                                           color=color))
                    state_counter_map[res_s.unique_id] += 1
                    cnt = state_counter_map[res_s.unique_id]
                    res_state_internal_id = f"{res_s.shortened_state_id(length=VisdccMultipleUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})_{path_cnt}"
                    color = None if not meta_data.is_empty() else VisdccMultipleUseCaseExecutionsViz.get_node_color_highlight()
                    states.append(self.transform_state(state=res_s,
                                                       internal_state_id=res_state_internal_id,
                                                       shortened_state_len=VisdccMultipleUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN,
                                                       color=color))

                    id_e, edge = self.transform_edge(trans, src_state_internal_id, res_state_internal_id, meta_data)
                    edges.append(edge)

                    last_res_s = res_s

                self.data[use_case_exec].append(dict(nodes=states, edges=edges, path=use_case_exec_path))

    @staticmethod
    def get_node_color_highlight():
        return dict(
            border=colorconstants.HEX_COLOR_RED,
            background=colorconstants.HEX_COLOR_WHITE,
            highlight=dict(border=colorconstants.HEX_COLOR_BLUE, background=colorconstants.HEX_COLOR_BLUE)
        )

    def transform_edge(self, trans, source_state_id, resulting_state_id, uc_meta_data):
        """
        Override transform_edge
        """
        id_e = f"{source_state_id} -> {resulting_state_id}"
        label = ""
        if uc_meta_data.has(metadata.META_DATA_ATD):
            label = f"<<{trans.action}\n'{uc_meta_data.get(metadata.META_DATA_ATD).target_descriptor}'>>"
        else:
            i_widget = trans.interacted_widget_o
            label = f"<{trans.action}>" if i_widget is None else f"<{trans.action}\n'{i_widget.displayed_text}' '{i_widget.hint_text}'>"
        edge = {
            'id': id_e,
            'from': f"{source_state_id}",
            'to': f"{resulting_state_id}",
            'label': label,
        }
        if not trans.successful:
            edge['color'] = dict(color=colorconstants.HEX_COLOR_ORANGE)
        elif uc_meta_data.is_empty():
            edge['color'] = dict(color=colorconstants.HEX_COLOR_RED)
        return id_e, edge

    def visualize_graph(self):
        ui_elem = []
        for i, use_case_exec in enumerate(self.data):
            d_list = self.data[use_case_exec]

            for path_cnt, d in enumerate(d_list):
                ui_elem.append(html.Hr())
                ui_elem.append(html.P(f"Use case #{i}.{path_cnt}: {use_case_exec.use_case.name}"))
                network = visdcc.Network(id=f"network_{i}_{path_cnt}",
                                         selection={'nodes': [], 'edges': []},
                                         options=BaseVisdccViz.get_options(heigth=self.GRAPH_HEIGHT, hierarchical_layout=True),
                                         data=dict(nodes=d['nodes'], edges=d['edges']))
                path = d['path']
                atds = path.get_filtered_meta_data_by_key(metadata.META_DATA_ATD)
                atds_info = [str(atd) for atd in atds]
                ui_elem.append(html.P(f"ATDs: {atds_info}"))
                container = dbc.Container(id=f"network_{i}_container_{path_cnt}",
                                          children=network,
                                          style={"border": "1px solid black"})
                ui_elem.append(container)
        return ui_elem
