# -*- coding: utf-8 -*-
import math
from typing import Set

from analysis.apphomestatesmap import APP_HOME_STATES_MAP
from graph import graph
from model.tagger.apphomestatetagger import AppHomeStateVerifiedUCETagger, AppHomeStateComputedUCETagger
from model.tagger.basestatetagger import TaggingMethod


class AppHomeStateTagManager(object):
    def __init__(self, exploration_model) -> None:
        self.exploration_model = exploration_model
        self.app_home_state_tagger_verified = AppHomeStateVerifiedUCETagger()
        self.app_home_state_tagger_computed = AppHomeStateComputedUCETagger()
        self.app_home_states_verified: Set[str] = None
        self.app_home_states_computed: Set[str] = None

    def get_app_home_states(self) -> Set[str]:
        # Tag the verified use case executions
        self.app_home_states_verified: Set[str] = self.app_home_state_tagger_verified.tag_states(self.exploration_model)
        # Tag the computed use case executions
        self.app_home_states_computed: Set[str] = self.app_home_state_tagger_computed.tag_states(self.exploration_model)

        app_home_states_all = self.app_home_states_verified.union(self.app_home_states_computed)
        return app_home_states_all

    def calc_distance(self) -> int:
        labeled_states = APP_HOME_STATES_MAP[self.exploration_model.package_name]

        app_home_states_all = self.app_home_states_verified.union(self.app_home_states_computed)
        # tagged_states = [self.exploration_model.uid_state_map[app_home_state]
        tagged_states = [app_home_state
                         for app_home_state in app_home_states_all
                         if app_home_state in self.exploration_model.uid_state_map]
        g: graph.Graph = self.exploration_model.use_case_base_graph

        # Minimum of all tagged states to labeled states
        # Either take the path length from (labeled to tagged) state or (tagged to labeled) state.
        # There might be no path one way.
        dist = math.inf
        for tagged_state in tagged_states:
            for labeled_state in labeled_states:
                if g.has_node(labeled_state) and g.has_node(tagged_state):
                    if g.has_path(labeled_state, tagged_state):
                        dist = min(dist, g.shortest_path_length(src=labeled_state, target=tagged_state))
                    if g.has_path(tagged_state, labeled_state):
                        dist = min(dist, g.shortest_path_length(src=tagged_state, target=labeled_state))

        assert dist < math.inf, f"Dist was: {dist}"

        return dist

    def get_tagging_method(self) -> TaggingMethod:
        return self.app_home_state_tagger_computed.tag_method
