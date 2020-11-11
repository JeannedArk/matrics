# -*- coding: utf-8 -*-
import itertools
from functools import lru_cache
from typing import List, Tuple

import networkx as nx

import metadata
from graph.baseoptimalpath import BaseOptimalPath
from graph.path import Path
from metadata import MetaData
from model.atd import ATD
from model.transition import Transition

MAX_COMBINATIONS = 10000


class MultiNodePathSolver(BaseOptimalPath):
    """
    Use Path class.
    """
    def __init__(self, exploration_model, use_case_path_exclusion_criterion):
        self.exploration_model = exploration_model
        self.use_case_path_exclusion_criterion = use_case_path_exclusion_criterion
        self.base_use_case_networkx_graph: nx.DiGraph = self.exploration_model.use_case_base_graph.networkx_graph
        # Nice idea, but super annoying to handle
        # fw = nx.floyd_warshall_predecessor_and_distance(self.networkx_g)
        # self.floyd_warshall_matrix_pred = fw[0]
        # self.floyd_warshall_matrix_dist = fw[1]

    def _find_path(self, start_node, transitions: List[Transition], atds: List[ATD]):
        # Check at first, if there is a path connecting all nodes
        if self.path_exist(transitions, start_node):
            # Check for acceptance
            first_node = transitions[0].source_state
            shortest_path_start = self.shortest_path(node1=start_node, node2=first_node)
            if self.use_case_path_exclusion_criterion.decide(shortest_path_start, from_home_state=True):
                return None

            path = Path()
            if len(transitions) == 1:
                trans1 = transitions[0]
                atd1: ATD = atds[0]
                data = {metadata.META_DATA_TRANSITION: trans1, metadata.META_DATA_ATD: atd1}
                meta_data_trans1 = [MetaData(data=data), MetaData()]
                path.append_path(nodes=[trans1.source_state, trans1.resulting_state],
                                 meta_data_elements=meta_data_trans1,
                                 count_dist=True)
            else:
                # Example:
                # perm = [
                #   Transition: b55cc47c-1fd2-3ebb-9985-cd5a9fe83ea0_0b1d10ca-459c-3fa4-a2c1-cc2575bdca6e
                #       -> 9d9007c6-5a03-33b2-a8fb-95a3dbcab398_a0dbdf62-d056-3164-b1b0-7edb6d67329a
                #   Transition: c1a4c313-221d-32c4-9f94-180b13eb9888_a4422e14-cb07-3aac-b8a5-adbb734846cd
                #       -> fd64ac6f-1e21-3cea-8fd6-77f6be42ea22_f518d57e-08b1-3019-a57e-5317b81405b5
                #   Transition: bd41911f-6a1b-3d8b-b4e2-d536e66bd962_72474130-172a-349d-9efd-2a2bcff81e9e
                #       -> 0c07d366-1ee5-3c8f-854e-d6878471ffe2_83d47a98-e99d-3aab-9d47-1032b5efea97
                # ]
                for i in range(len(transitions) - 1):
                    trans1 = transitions[i]
                    trans2 = transitions[i + 1]
                    trans1_result_node = trans1.resulting_state
                    trans2_source_node = trans2.source_state
                    atd1: ATD = atds[i]
                    atd2: ATD = atds[i + 1]

                    # Add the source state to the resulting state of trans1 for the first iteration, because it hasn't
                    # been added yet and we don't need this step for the following iterations
                    if i == 0:
                        data = {metadata.META_DATA_TRANSITION: trans1, metadata.META_DATA_ATD: atd1}
                        meta_data_trans1 = [MetaData(data=data), MetaData()]
                        # Add here meta data
                        path.append_path(nodes=[trans1.source_state, trans1.resulting_state],
                                         meta_data_elements=meta_data_trans1,
                                         count_dist=True)
                    shortest_p = self.shortest_path(node1=trans1_result_node, node2=trans2_source_node)
                    # Check for acceptance
                    if self.use_case_path_exclusion_criterion.decide(shortest_p):
                        return None
                    meta_data_p = [MetaData() for node in shortest_p]
                    path.append_path(nodes=shortest_p,
                                     meta_data_elements=meta_data_p,
                                     count_dist=True)
                    data = {metadata.META_DATA_TRANSITION: trans2, metadata.META_DATA_ATD: atd2}
                    meta_data_trans2 = [MetaData(data=data), MetaData()]
                    path.append_path(nodes=[trans2.source_state, trans2.resulting_state],
                                     meta_data_elements=meta_data_trans2,
                                     count_dist=True)

            # Add the path from the start_node to the first node of the permutations
            path.prepend_path(nodes=shortest_path_start)

            return path
        else:
            return None

    def find_path(self, transitions_w_atds_ls: List[Tuple[Transition, ATD]], start_node):
        """
        Find path by transitions.
        """
        assert transitions_w_atds_ls, "Expected transitions to be greater than 0"
        paths = []

        permutations = itertools.permutations(transitions_w_atds_ls, )
        for perm in itertools.islice(permutations, 0, MAX_COMBINATIONS):
            # Create one list with the start node as head
            transitions: List[Transition] = [tple[0] for tple in perm]
            atds: List[ATD] = [tple[1] for tple in perm]
            path = self._find_path(start_node, transitions, atds)
            if path is not None:
                paths.append(path)

        paths.sort()
        # Return the best path if possible in terms of length
        return paths[0] if paths else None

    def path_exist(self, transitions, start_node):
        assert transitions
        if not self.has_path(start_node, transitions[0].source_state):
            # There exists no path
            return False

        for i in range(len(transitions) - 1):
            """
            [A,B] [C,D] [D,F]
            """
            trans1 = transitions[i]
            trans2 = transitions[i + 1]
            if not self.has_path(trans1.resulting_state, trans2.source_state):
                # There exists no path
                return False

        return True

    @lru_cache(maxsize=4096)
    def has_path(self, node1, node2):
        return nx.has_path(self.base_use_case_networkx_graph, source=node1, target=node2)

    @lru_cache(maxsize=4096)
    def shortest_path(self, node1, node2):
        return nx.shortest_path(self.base_use_case_networkx_graph, source=node1, target=node2)
