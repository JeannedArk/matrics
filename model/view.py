# -*- coding: utf-8 -*-
from typing import Set, List

import numpy as np

import metadata
from graph.path import Path
from model.har import HarEntry
from model.state import State


class TraceView(object):
    def __init__(self, trace, start_idx: int):
        assert start_idx is not None and start_idx > 0, f"Start index was: {start_idx}"
        self.trace = trace
        # Include only the transitions beginning from the tagged start state
        self.transitions = trace.transitions[start_idx:]
        assert len(self.transitions) > 0


class View(object):
    def __init__(self, use_case_execution):
        self.use_case_execution = use_case_execution
        self.trace_views = [TraceView(trace, self.use_case_execution.start_index) for trace in self.use_case_execution.get_playback_traces()]
        self.transitions_view_len = len(self.trace_views[0].transitions)

    def data_op_func(self, data):
        return np.mean(data)

    # def modify_transitions(self):
    #     transitions = [trans.copy() for trans in self.trace_views[0].transitions]
    #     for trans in transitions:
    #         pass
    #     self.transitions = transitions
    #
    # def modify_network_entries(self):
    #     for i in range(self.transitions_view_len):
    #         np.mean(len(trace.transitions[i].network_page.ref_entries)
    #                 for trace in self.trace_views
    #                 if trace.transitions[i].network_page is not None)
    #
    #         pass
    #     trace_entries = [np.mean(len(trace.transitions[i].network_page.ref_entries)
    #                              for trace in self.trace_views
    #                              if trace.transitions[i].network_page is not None)
    #                      for i in range(len(self.trace_views[0].transitions))]
    #     return trace_entries

    def get_transitions(self):
        return self.trace_views[0].transitions

    def get_states(self) -> Set[State]:
        states = set()
        for trans in self.trace_views[0].transitions:
            states.add(trans.source_state_o)
            states.add(trans.resulting_state_o)
        return states

    def get_all_network_entries(self) -> List[HarEntry]:
        return [entry
                for i in range(self.transitions_view_len)
                for trace in self.trace_views
                if trace.transitions[i].network_page is not None
                for entry in trace.transitions[i].network_page.ref_entries]

    def get_network_timings_wait(self):
        # trace_entries = [self.data_op_func(entry.timings.wait
        #                                    for trace in self.trace_views
        #                                    if trace.transitions[i].network_page is not None
        #                                    for entry in trace.transitions[i].network_page.ref_entries)
        #                  for i in range(self.transitions_view_len)]
        trace_entries = []
        for i in range(self.transitions_view_len):
            waits = [entry.timings.wait
                     for trace in self.trace_views
                     if trace.transitions[i].network_page is not None
                     for entry in trace.transitions[i].network_page.ref_entries]
            # Only use the data_op_func if there are values inserted, otherwise the function would raise an
            # exception. Therefore, add 0.
            val = self.data_op_func(waits) if waits else 0
            trace_entries.append(val)

        return trace_entries

    def get_number_network_entries(self) -> int:
        """
        Trace 0:    [10     10      10]
        Trace 1:    [9      9       9]
        Trace 2:    [2      2       2]
        View:       [7      7       7]

        7 = 21 / 3
        """
        # trace_entries = [self.data_op_func(len(trace.transitions[i].network_page.ref_entries)
        #                                    for trace in self.trace_views
        #                                    if trace.transitions[i].network_page is not None)
        #                  ]
        trace_entries = []
        for i in range(self.transitions_view_len):
            values_tmp = []
            for trace in self.trace_views:
                if trace.transitions[i].network_page is not None:
                    values_tmp.append(len(trace.transitions[i].network_page.ref_entries))
            # Only use the data_op_func if there are values inserted, otherwise the function would raise an
            # exception. Therefore, add 0.
            val = self.data_op_func(values_tmp) if values_tmp else 0
            trace_entries.append(val)

        return sum(trace_entries)

    def get_number_network_errors(self) -> int:
        """
        Trace 0:    [10     10      10]
        Trace 1:    [9      9       9]
        Trace 2:    [2      2       2]
        View:       [7      7       7]
        """
        trace_entries = []
        for i in range(self.transitions_view_len):
            values_tmp = []
            for trace in self.trace_views:
                if trace.transitions[i].network_page is not None:
                    number_errors = sum(1 for entry in trace.transitions[i].network_page.ref_entries
                                        if 400 <= entry.response.status < 600)
                    values_tmp.append(number_errors)
            # Only use the data_op_func if there are values inserted, otherwise the function would raise an
            # exception. Therefore, add 0.
            val = self.data_op_func(values_tmp) if values_tmp else 0
            trace_entries.append(val)

        return sum(trace_entries)

    def get_network_payload_size_request(self):
        trace_entries = []
        for i in range(self.transitions_view_len):
            payload_sizes = [entry.request.bodySize
                             for trace in self.trace_views
                             if trace.transitions[i].network_page is not None
                             for entry in trace.transitions[i].network_page.ref_entries
                             if entry.request.bodySize >= 0]

            # Only use the data_op_func if there are values inserted, otherwise the function would raise an
            # exception. Therefore, add 0.
            val = self.data_op_func(payload_sizes) if payload_sizes else 0
            trace_entries.append(val)

        return trace_entries

    def get_network_payload_size_response(self):
        trace_entries = []
        for i in range(self.transitions_view_len):
            payload_sizes = [entry.response.bodySize
                             for trace in self.trace_views
                             if trace.transitions[i].network_page is not None
                             for entry in trace.transitions[i].network_page.ref_entries
                             if entry.response.bodySize >= 0]

            # Only use the data_op_func if there are values inserted, otherwise the function would raise an
            # exception. Therefore, add 0.
            val = self.data_op_func(payload_sizes) if payload_sizes else 0
            trace_entries.append(val)

        return trace_entries

    def get_features(self) -> List[str]:
        uce_path: Path = self.use_case_execution.get_verified_computed_path()
        return [meta_data.target_descriptor
                for meta_data in uce_path.get_filtered_meta_data_by_key(metadata.META_DATA_ATD)]
