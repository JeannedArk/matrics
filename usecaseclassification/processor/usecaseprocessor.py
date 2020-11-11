# -*- coding: utf-8 -*-
import itertools
from abc import ABCMeta, abstractmethod

import metadata
from graph.path import Path
from metadata import MetaData
from model.transition import Transition


class UseCaseProcessor(metaclass=ABCMeta):

    @staticmethod
    def get_combinations(entry_list_map):
        """
        Example:
        {
            "Feature 1": [A, B]
            "Feature 2": [C, D, E]
        }
        return [ [A, C], [A, D], [A, E], [B, C], [B, D], [B, E] ]
        """
        entries_list = [entries
                        for entries in entry_list_map.values()
                        if entries]
        return itertools.product(*entries_list)

    @abstractmethod
    def compute_use_case_executions(self):
        pass

    def append_terminate(self, path: Path, uid_state_map, resulting_end_state):
        assert path.nodes
        last_node = path.nodes[-1]
        last_node_o = uid_state_map[last_node]
        assert last_node_o is not None, f"Did not find an object for node {last_node_o}"
        resulting_end_state_o = uid_state_map[resulting_end_state]
        assert resulting_end_state_o is not None, f"Did not find an object for node {resulting_end_state}"
        trans = Transition.construct_terminate_transition(source_state_o=last_node_o, resulting_state_o=resulting_end_state_o)
        meta_data = [MetaData(data={metadata.META_DATA_TRANSITION: trans}), MetaData()]
        path.append_path(nodes=[last_node, resulting_end_state], meta_data_elements=meta_data, count_dist=False)
        return path
