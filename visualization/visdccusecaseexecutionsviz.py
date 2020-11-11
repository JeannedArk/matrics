# -*- coding: utf-8 -*-
import collections
from typing import List, Dict

import dash_html_components as html
import dash_bootstrap_components as dbc
import visdcc

import colorconstants
import metadata
from graph.path import Path
from metadata import MetaData
from usecaseclassification.usecaseexecution import UseCaseExecution
from visualization.basevisdccviz import BaseVisdccViz


USE_CASE_EXECUTION_GRAPH_HTML_ID = 'vis-use-case-execution'


class VisdccUseCaseExecutionsViz(BaseVisdccViz):
    GRAPH_HEIGHT = "300px"
    SHORTENED_STATE_NAME_LEN = 4

    def __init__(self, exploration_model, mark_app_home_states):
        super().__init__(USE_CASE_EXECUTION_GRAPH_HTML_ID)
        self.mark_app_home_states = mark_app_home_states
        self.data: Dict[UseCaseExecution, Dict] = collections.defaultdict(dict)
        for use_case_exec in exploration_model.use_case_execution_manager.get_use_case_executions(filter_not_successful=True):
            states, edges = self.get_data_from_use_case_execution(use_case_exec, self.mark_app_home_states)
            assert states is not None
            assert edges is not None
            self.data[use_case_exec] = dict(nodes=states, edges=edges)

    def get_data_from_use_case_execution(self, use_case_exec, mark_app_home_states):
        uc_exec_trace = use_case_exec.get_representative_trace() if use_case_exec.is_verified() else use_case_exec.get_best_computed_path().trace
        assert uc_exec_trace is not None
        app_home_state: str = uc_exec_trace.app_home_state
        uc_exec_seq = uc_exec_trace.sequence
        _, transitions, _ = uc_exec_seq.get_flatted_representation()
        meta_data_ls: List[MetaData] = [MetaData() for trans in transitions] if use_case_exec.is_verified() else uc_exec_trace.meta_data
        assert len(transitions) == len(meta_data_ls), f"Transitions len was {len(transitions)}, meta data len was {meta_data_ls}"
        state_counter_map = collections.defaultdict(int)
        states = []
        # We don't need process_edges for this case
        edges = []

        last_res_s = None
        for i, trans in enumerate(transitions):
            meta_data: MetaData = meta_data_ls[i]
            src_s = trans.source_state_o
            cnt = state_counter_map[src_s.unique_id]
            src_state_internal_id = f"{src_s.shortened_state_id(length=VisdccUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})"
            res_s = trans.resulting_state_o

            if last_res_s != src_s:
                state_counter_map[src_s.unique_id] += 1
                cnt = state_counter_map[src_s.unique_id]
                src_state_internal_id = f"{src_s.shortened_state_id(length=VisdccUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})"
                color = None if not meta_data.is_empty() else VisdccUseCaseExecutionsViz.get_node_color_highlight()
                is_app_home_state = mark_app_home_states and src_s.unique_id == app_home_state
                states.append(self.transform_state(state=src_s,
                                                   internal_state_id=src_state_internal_id,
                                                   shortened_state_len=VisdccUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN,
                                                   color=color,
                                                   is_app_home_state=is_app_home_state))
            state_counter_map[res_s.unique_id] += 1
            cnt = state_counter_map[res_s.unique_id]
            res_state_internal_id = f"{res_s.shortened_state_id(length=VisdccUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN)}_({cnt})"
            color = None if not meta_data.is_empty() else VisdccUseCaseExecutionsViz.get_node_color_highlight()
            is_app_home_state = mark_app_home_states and res_s.unique_id == app_home_state
            states.append(self.transform_state(state=res_s,
                                               internal_state_id=res_state_internal_id,
                                               shortened_state_len=VisdccUseCaseExecutionsViz.SHORTENED_STATE_NAME_LEN,
                                               color=color,
                                               is_app_home_state=is_app_home_state))

            id_e, edge = self.transform_use_case_execution_edge(trans, src_state_internal_id, res_state_internal_id, meta_data)
            edges.append(edge)

            last_res_s = res_s
        return states, edges

    @staticmethod
    def get_node_color_highlight():
        return dict(
            border=colorconstants.HEX_COLOR_RED,
            background=colorconstants.HEX_COLOR_WHITE,
            highlight=dict(border=colorconstants.HEX_COLOR_BLUE, background=colorconstants.HEX_COLOR_BLUE)
        )

    def transform_use_case_execution_edge(self, trans, source_state_id, resulting_state_id, uc_meta_data):
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
            d = self.data[use_case_exec]
            ui_elem.append(html.Hr())
            if use_case_exec.is_verified():
                badge = dbc.Badge("verified", color="success", className="mr-1")
            else:
                badge = dbc.Badge("computed", color="dark", className="mr-1")
            ui_elem.append(html.P([f"Use case #{i}: {use_case_exec.use_case.name} ({use_case_exec.playback_trace_id}) ", badge]))
            network = visdcc.Network(id=f"network_{i}",
                                     selection={'nodes': [], 'edges': []},
                                     options=BaseVisdccViz.get_options(heigth=self.GRAPH_HEIGHT, hierarchical_layout=True),
                                     data=d)
            if use_case_exec.is_computed():
                # Implicitly using the best path
                path = use_case_exec.get_best_computed_path()
                atds = path.get_filtered_meta_data_by_key(metadata.META_DATA_ATD)
                atds_info = [str(atd) for atd in atds]
                ui_elem.append(html.P(f"ATDs: {atds_info}"))
            container = dbc.Container(id=f"network_{i}_container",
                                      children=network,
                                      style={"border": "1px solid black"})
            ui_elem.append(container)
        return ui_elem
