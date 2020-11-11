# -*- coding: utf-8 -*-
import math
import operator
from functools import lru_cache
from typing import List, Optional

import networkx as nx

from datatypes.orderedset import OrderedSet
from graph.transformer.visualsimilaritymerger import VisualSimilarityMerger
from model.state import State
from usecaseclassification.tsequence import TSequence


MAX_N = 6


class Graph(object):
    def __init__(self, package_name: str, states: OrderedSet, transitions, home_state: State, filter_not_connected_subgraphs=True):
        self.package_name = package_name
        self.home_state = home_state
        self.filter_not_connected_subgraphs = filter_not_connected_subgraphs
        self.networkx_graph, self.states, self.transitions = self.construct_networkx_graph(states, transitions)
        self.sequence = TSequence.construct_from_transitions(self.transitions)
        self.app_home_states: List[State] = []
        self.merger: Optional[VisualSimilarityMerger] = None

    def construct_networkx_graph(self, states_orig: OrderedSet, transitions_orig) -> (nx.DiGraph, list, list):
        home_state_id = self.home_state.unique_id
        G = nx.DiGraph()

        for trans in transitions_orig:
            # Beware that transitions with the same source and resulting state will override the former transition
            G.add_edge(trans.source_state_o.unique_id,
                       trans.resulting_state_o.unique_id,
                       object=trans)

                # TODO creates a KeyError
                # Add states that only belong to an edge
                # G.add_node(trans.source_state_o, object=trans.source_state_o)
                # G.add_node(trans.resulting_state_o, object=trans.resulting_state_o)

        for state in states_orig:
            G.add_node(state.unique_id, object=state)

        states = states_orig
        transitions = []
        transitions_unique_set = set()
        if self.filter_not_connected_subgraphs:
            for trans in transitions_orig:
                source_state_id = trans.source_state_o.unique_id
                resulting_state_id = trans.resulting_state_o.unique_id

                if G.has_node(source_state_id):
                    if nx.has_path(G, source=home_state_id, target=source_state_id):
                        # Check if the transition already exists, we want to filter duplicates
                        trans_str = f"{trans.source_state} {trans.resulting_state} {trans.interacted_widget} {trans.action}"
                        if trans_str not in transitions_unique_set:
                            transitions_unique_set.add(trans_str)
                            transitions.append(trans)
                    else:
                        G.remove_node(source_state_id)
                        states.remove(trans.source_state_o)
                if G.has_node(resulting_state_id):
                    if not nx.has_path(G, source=home_state_id, target=resulting_state_id):
                        G.remove_node(resulting_state_id)
                        states.remove(trans.resulting_state_o)

            # We have to remove single unconnected states. I am missing something in the previous step, I don't
            # know what it is.
            states_copy = OrderedSet(s for s in states)
            for state in states_copy:
                if not nx.has_path(G, source=home_state_id, target=state.unique_id):
                    states.remove(state)
        else:
            states = states_orig
            transitions = transitions_orig

        # print(f"Optimal networkx graph edges: {len(G.edges)}")

        # Edges and transitions can be zero for failed playbacks
        assert G.nodes
        # assert G.edges
        if not G.edges:
            print(f"Edges in graph were 0")
        assert states
        # assert transitions
        if not transitions:
            print(f"Transitions in graph were 0")

        return G, states, transitions

    def rebuild_networkx_graph(self):
        G = nx.DiGraph()
        for trans in self.transitions:
            # Beware that transitions with the same source and resulting state will override the former transition
            G.add_edge(trans.source_state_o.unique_id,
                       trans.resulting_state_o.unique_id,
                       object=trans)

                # TODO creates a KeyError
                # Add states that only belong to an edge
                # G.add_node(trans.source_state_o, object=trans.source_state_o)
                # G.add_node(trans.resulting_state_o, object=trans.resulting_state_o)

        for state in self.states:
            G.add_node(state.unique_id, object=state)

        self.networkx_graph = G
        self.sequence = TSequence.construct_from_transitions(self.transitions)

        assert len(self.states) == len(self.networkx_graph.nodes),\
            f"Expected size to be equal, states: {len(self.states)} networkx states: {len(self.networkx_graph.nodes)}"

    def add_app_home_states(self, app_home_states):
        self.app_home_states.extend(app_home_states)

    @lru_cache(maxsize=1)
    def k_vertex_connectivity(self):
        """
        https://en.wikipedia.org/wiki/K-vertex-connected_graph
        """
        return nx.node_connectivity(self.networkx_graph)

    @lru_cache(maxsize=1)
    def k_edge_connectivity(self):
        """
        https://en.wikipedia.org/wiki/K-edge-connected_graph
        """
        return nx.edge_connectivity(self.networkx_graph)

    @lru_cache(maxsize=1)
    def density(self):
        """
        https://en.wikipedia.org/wiki/Dense_graph
        https://networkx.github.io/documentation/latest/reference/generated/networkx.classes.function.density.html
        """
        return nx.density(self.networkx_graph)

    @lru_cache(maxsize=1)
    def diameter(self):
        """
        http://mathworld.wolfram.com/GraphDiameter.html
        https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.distance_measures.diameter.html

        networkx.exception.NetworkXError: Found infinite path length because the digraph is not strongly connected
        """
        return nx.diameter(self.networkx_graph)

    @lru_cache(maxsize=1)
    def num_nodes(self):
        return len(self.networkx_graph.nodes)

    @lru_cache(maxsize=1)
    def num_edges(self):
        return len(self.networkx_graph.edges)

    @lru_cache(maxsize=1)
    def graph_depth_from_home_state(self) -> List[int]:
        return [v for v in (nx.single_source_shortest_path_length(G=self.networkx_graph, source=self.home_state.unique_id)).values()]

    @lru_cache(maxsize=1)
    def average_shortest_path_length(self) -> int:
        """
        We have to transform the graph to an undirected one. However, his results in a deepcopy and raises an exception.
        """
        return nx.average_shortest_path_length(G=nx.DiGraph(self.networkx_graph).to_undirected())

    def shortest_path_length(self, src: str, target: str):
        return nx.shortest_path_length(G=self.networkx_graph, source=src, target=target)

    def has_node(self, node: str) -> bool:
        return self.networkx_graph.has_node(node)

    def has_path(self, src: str, target: str):
        return nx.has_path(G=self.networkx_graph, source=src, target=target)

    def indegree_graph(self) -> float:
        """
        Not used anymore as it useless on an app aggregation level.

        https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.DiGraph.in_degree.html
        """
        node_mapping = self.networkx_graph.in_degree()
        total = sum(t[1] for t in node_mapping)
        return total
        # return total / len(node_mapping)

    def max_indegree(self) -> int:
        return max(t[1] for t in self.networkx_graph.in_degree())

    def max_indegree_nodes(self, max_n=MAX_N) -> List[str]:
        node_mapping = self.networkx_graph.in_degree()
        top_n_elements = sorted(node_mapping, key=operator.itemgetter(1))[-max_n:]
        return list(reversed([node for node, indegree in top_n_elements]))

    def outdegree_graph(self) -> float:
        """
        Not used anymore as it useless on an app aggregation level.
        """
        node_mapping = self.networkx_graph.out_degree()
        total = sum(t[1] for t in node_mapping)
        return total
        # return total / len(node_mapping)

    def max_outdegree(self) -> int:
        return max(t[1] for t in self.networkx_graph.out_degree())

    def max_outdegree_nodes(self, max_n=MAX_N) -> List[str]:
        node_mapping = self.networkx_graph.out_degree()
        top_n_elements = sorted(node_mapping, key=operator.itemgetter(1))[-max_n:]
        return list(reversed([node for node, outdegree in top_n_elements]))

    def merge_graph(self):
        self.merger = VisualSimilarityMerger(self)
        self.merger.transform()
        self.rebuild_networkx_graph()
        print(f"Final model size after post-processing: {len(self.states)}")

    def dump_states_to_file(self):
        # TODO
        pass
