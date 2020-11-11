# -*- coding: utf-8 -*-
import visdcc

from visualization.basevisdccviz import BaseVisdccViz


OVERALL_GRAPH_HTML_ID = 'vis-model-overall'
USE_CASE_BASE_GRAPH_HTML_ID = 'vis-model-base-use-case'
USE_CASE_BASE_TRANSFORMED_GRAPH_HTML_ID = 'vis-model-transformed-base-use-case'
USE_CASE_BASE_UNMODIFIED_GRAPH_HTML_ID = 'vis-model-unmodified-base-use-case'
USE_CASE_BASE_DEFAULT_GRAPH_HTML_ID = 'vis-model-default-base-use-case'


ALWAYS_SHOW_APP_HOME_STATES = False


class GraphBasedVisdccViz(BaseVisdccViz):
    def __init__(self, graph, ui_html_id, mark_app_home_states):
        super().__init__(ui_html_id)
        self.graph = graph
        self.mark_app_home_states = mark_app_home_states
        transitions = self.graph.transitions
        self.edges, self.id_edge_map = self.process_edges(transitions)
        self.states = [self.transform_state(state=state,
                                            is_app_home_state=(self.mark_app_home_states and any(state == ah_state for ah_state in self.graph.app_home_states)))
                       for state in self.graph.states]
        self.data = dict(nodes=self.states, edges=self.edges)

    def visualize_graph(self):
        ui_elems = [
            visdcc.Network(id=self.ui_html_id,
                           selection={'nodes': [], 'edges': []},
                           options=BaseVisdccViz.get_options(),
                           data=self.data),
        ]
        return ui_elems


class VisdccOverallGraphViz(GraphBasedVisdccViz):
    def __init__(self, graph, mark_app_home_states=False):
        super().__init__(graph, OVERALL_GRAPH_HTML_ID, mark_app_home_states)


class VisdccUseCaseBaseGraphViz(GraphBasedVisdccViz):
    def __init__(self, graph, mark_app_home_states=False):
        super().__init__(graph, USE_CASE_BASE_GRAPH_HTML_ID, mark_app_home_states)


class VisdccUseCaseBaseTransformedGraphViz(GraphBasedVisdccViz):
    def __init__(self, graph, mark_app_home_states=False):
        super().__init__(graph, USE_CASE_BASE_TRANSFORMED_GRAPH_HTML_ID, mark_app_home_states)


class VisdccUseCaseBaseUnmodifiedGraphViz(GraphBasedVisdccViz):
    def __init__(self, graph, mark_app_home_states=False):
        super().__init__(graph, USE_CASE_BASE_UNMODIFIED_GRAPH_HTML_ID, mark_app_home_states)


class VisdccUseCaseBaseDefaultGraphViz(GraphBasedVisdccViz):
    def __init__(self, graph, mark_app_home_states):
        super().__init__(graph, USE_CASE_BASE_DEFAULT_GRAPH_HTML_ID, mark_app_home_states)
