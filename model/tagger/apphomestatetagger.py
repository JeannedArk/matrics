# -*- coding: utf-8 -*-
from typing import Set, Optional

from model.tagger.basestatetagger import BaseStateTagger, TaggingMethod


class StateWrapper(object):
    def __init__(self, state_id: str, exploration_model=None, graph=None):
        self.state_id = state_id
        self.exploration_model = exploration_model
        self.graph = graph
        assert exploration_model is not None or graph is not None

    def __str__(self) -> str:
        return f"StateWrapper(state_id={self.state_id} is_home_screen={self.is_home_screen()})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_home_screen(self) -> bool:
        if self.exploration_model is not None:
            state = self.exploration_model.uid_state_map[self.state_id]
            return state.is_home_screen
        else:
            return self.graph.home_state.unique_id == self.state_id


def select_login_use_case_executions(use_case_execution):
    return use_case_execution.use_case.name.lower().startswith("login")


class AppHomeStateComputedUCETagger(BaseStateTagger):
    DENSITY_THRESHOLD = 0.084

    def tag_along_use_case_execution(self, exploration_model, use_case_executions) -> Set[StateWrapper]:
        if not use_case_executions:
            return set()

        idx = 0
        common_state_bool = True
        common_state: Optional[str] = None
        # We only use the best computed paths
        uce_paths = [uce.get_best_computed_path() for uce in use_case_executions]
        while common_state_bool and all(len(uce_path.nodes) > idx for uce_path in uce_paths):
            next_states = set(uce_path.nodes[idx] for uce_path in uce_paths)
            common_state_bool = len(next_states) == 1
            idx += 1
            if common_state_bool:
                common_state = next_states.pop()
        # Tag the state
        for uce_path in uce_paths:
            uce_path.trace.app_home_state = common_state

        assert common_state is not None

        state_wrapper = StateWrapper(state_id=common_state, exploration_model=exploration_model)

        return set([state_wrapper])

    def tag_degree_based(self, exploration_model, use_case_executions) -> Set[StateWrapper]:
        max_n = 1
        max_n_limit = 30
        intersection = []
        while not intersection or max_n >= max_n_limit:
            states_max_indegree = exploration_model.use_case_base_graph.max_indegree_nodes(max_n=max_n)
            states_max_outdegree = exploration_model.use_case_base_graph.max_outdegree_nodes(max_n=max_n)
            states_max_indegree_set = set(states_max_indegree)
            states_max_outdegree_set = set(states_max_outdegree)
            intersection = states_max_indegree_set.intersection(states_max_outdegree_set)
            max_n += 1

        assert len(intersection) == 1, f"Intersection size was: {len(intersection)}"
        app_home_state = intersection.pop()
        state_wrapper = StateWrapper(state_id=app_home_state, exploration_model=exploration_model)

        for uce in use_case_executions:
            path = uce.get_best_computed_path()
            path.trace.app_home_state = app_home_state

        return set([state_wrapper])

    def tag_first_state_in_use_case_execution(self, exploration_model, use_case_executions) -> Set[StateWrapper]:
        tagged_states = set()
        # We only use the best computed paths
        uce_paths = [uce.get_best_computed_path() for uce in use_case_executions]

        for uce_path in uce_paths:
            node = uce_path.nodes[1]
            # Tag the state
            uce_path.trace.app_home_state = node
            state_wrapper = StateWrapper(state_id=node, exploration_model=exploration_model)
            tagged_states.add(state_wrapper)

        return tagged_states

    def tag_states(self, exploration_model) -> Set[str]:
        app_home_states = set()
        app_home_states_login = set()
        uc_executions = list(filter(lambda uce: not select_login_use_case_executions(uce),
                                    exploration_model.use_case_execution_manager.get_computed_use_case_executions()))
        uc_executions_login = list(filter(lambda uce: select_login_use_case_executions(uce),
                                          exploration_model.use_case_execution_manager.get_computed_use_case_executions()))
        uc_executions_all = uc_executions + uc_executions_login

        if uc_executions_all:
            density = exploration_model.use_case_base_graph.density()
            avg_indegree = exploration_model.use_case_base_graph.indegree_graph()
            max_indegree = exploration_model.use_case_base_graph.max_indegree()
            avg_outdegree = exploration_model.use_case_base_graph.outdegree_graph()
            max_outdegree = exploration_model.use_case_base_graph.max_outdegree()

            print(f"AppHomeStateComputedUCETagger density={density} avg indegree={avg_indegree} max indegree={max_indegree} avg outdegree={avg_outdegree} max outdegree={max_outdegree}")

            # if max_indegree > 5 * avg_indegree and density >= AppHomeStateComputedUCETagger.DENSITY_THRESHOLD:
            if density >= AppHomeStateComputedUCETagger.DENSITY_THRESHOLD:
                print(f"Density based tagging: {exploration_model.package_name}")
                self.tag_method = TaggingMethod.DENSITY
                app_home_states = self.tag_degree_based(exploration_model, uc_executions_all)
            else:
                print(f"Use case based tagging: {exploration_model.package_name}")
                self.tag_method = TaggingMethod.UCE
                app_home_states = self.tag_along_use_case_execution(exploration_model, uc_executions)
                app_home_states_login = self.tag_along_use_case_execution(exploration_model, uc_executions_login)

            assert not uc_executions or (uc_executions and len(app_home_states) == 1), f"app_home_states size was: {len(app_home_states)}"
            # If the tag strategies were not successful (=identifying home state), then just tag the first state
            # of the use case execution
            if any(s.is_home_screen() for s in app_home_states):
                app_home_states = self.tag_first_state_in_use_case_execution(exploration_model, uc_executions)
            if any(s.is_home_screen() for s in app_home_states_login):
                app_home_states_login = self.tag_first_state_in_use_case_execution(exploration_model, uc_executions_login)

            app_home_states_all = app_home_states.union(app_home_states_login)
            self.check_post_conditions(exploration_model, app_home_states_all)

        return set(state.state_id for state in app_home_states)
        # return app_home_states

    def check_post_conditions(self, exploration_model, app_home_states):
        assert app_home_states, f"app_home_states was {app_home_states}"

        # Every use case execution should have a tagged app home state
        for uce in exploration_model.use_case_execution_manager.get_computed_use_case_executions():
            uce_path = uce.get_best_computed_path()
            assert uce_path.trace.app_home_state is not None and uce_path.trace.app_home_state != ""

        assert all(not tagged_state.is_home_screen() for tagged_state in app_home_states)


class AppHomeStateVerifiedUCETagger(BaseStateTagger):
    """
    TODO We do not use the density based tagging:
    TODO Think about merged graphs
    """

    DENSITY_THRESHOLD = 0.084

    def __init__(self) -> None:
        super().__init__()
        self.tag_method = TaggingMethod.UCE

    def tag_along_use_case_execution(self, use_case_executions) -> Set[StateWrapper]:
        if not use_case_executions:
            return set()

        idx = 0
        common_state_bool = True
        # TODO representative trace
        common_state_tmp = None
        uce_traces = [uce.get_representative_trace() for uce in use_case_executions]
        while common_state_bool and all(len(uce_trace.transitions) > idx for uce_trace in uce_traces):
            next_states = set(uce_trace.transitions[idx].source_state_o for uce_trace in uce_traces)
            common_state_bool = len(next_states) == 1
            idx += 1
            if common_state_bool:
                common_state_tmp = next_states.pop()
        # Tag the state
        for uce in use_case_executions:
            self.tag_use_case_execution(uce, idx - 1)
        common_state = common_state_tmp.unique_id
        state_wrapper = StateWrapper(state_id=common_state,
                                     exploration_model=use_case_executions[0].get_representative_exploration_model())

        return set([state_wrapper])

    def tag_degree_based(self, exploration_model, use_case_executions) -> Set[StateWrapper]:
        """
        NOT USED
        """
        max_n = 1
        max_n_limit = 30
        intersection = []
        while not intersection or max_n >= max_n_limit:
            states_max_indegree = exploration_model.use_case_base_graph.max_indegree_nodes(max_n=max_n)
            states_max_outdegree = exploration_model.use_case_base_graph.max_outdegree_nodes(max_n=max_n)
            states_max_indegree_set = set(states_max_indegree)
            states_max_outdegree_set = set(states_max_outdegree)
            intersection = states_max_indegree_set.intersection(states_max_outdegree_set)
            max_n += 1

        assert len(intersection) == 1, f"Intersection size was: {len(intersection)}"
        app_home_state = intersection.pop()

        for uce in use_case_executions:
            trace = uce.get_representative_trace()
            states = [trans.source_state_o.unique_id for trans in trace.transitions]
            # TODO not true because of the merged use case base graph and the not merged uce
            # assert any(state == app_home_state for state in states)
            trace.app_home_state = app_home_state
        state_wrapper = StateWrapper(state_id=app_home_state, graph=exploration_model.use_case_base_graph)

        return set([state_wrapper])

    def tag_first_state_in_use_case_execution(self, use_case_executions) -> Set[StateWrapper]:
        index = 1
        tagged_states = set()
        # TODO representative trace
        for uce in use_case_executions:
            uce_trace = uce.get_representative_trace()
            state = uce_trace.transitions[index].source_state_o
            # Tag the state
            self.tag_use_case_execution(uce, index)
            uce_trace.app_home_state = state.unique_id
            state_wrapper = StateWrapper(state_id=state.unique_id, exploration_model=uce.get_representative_exploration_model())
            tagged_states.add(state_wrapper)

        return tagged_states

    def tag_states(self, exploration_model) -> Set[str]:
        app_home_states = set()
        app_home_states_login = set()
        app_home_states_all = set()
        uc_executions = list(filter(lambda uce: not select_login_use_case_executions(uce) and uce.is_verified(),
                                    exploration_model.use_case_execution_manager.use_case_executions))
        uc_executions_login = list(filter(lambda uce: select_login_use_case_executions(uce) and uce.is_verified(),
                                          exploration_model.use_case_execution_manager.use_case_executions))
        uc_executions_all = uc_executions + uc_executions_login
        # if exploration_model.use_case_base_graph.density() >= AppHomeStateVerifiedUCETagger.DENSITY_THRESHOLD:
        #     print(f"Density based: {exploration_model.package_name}")
        #     app_home_states = self.tag_degree_based(exploration_model, uc_executions_all)
        #     assert len(app_home_states) == 1, f"app_home_states size was: {len(app_home_states)}"
        # else:
        #     pass
        if uc_executions_all:
            print(f"Use case based tagging: {exploration_model.package_name}")
            app_home_states = self.tag_along_use_case_execution(uc_executions)
            app_home_states_login = self.tag_along_use_case_execution(uc_executions_login)

            # If the tag strategies were not successful (=identifying home state), then just tag the first state
            # of the use case execution
            if any(s.is_home_screen() for s in app_home_states):
                app_home_states = self.tag_first_state_in_use_case_execution(uc_executions)
            if any(s.is_home_screen() for s in app_home_states_login):
                app_home_states_login = self.tag_first_state_in_use_case_execution(uc_executions_login)

            app_home_states_all = app_home_states.union(app_home_states_login)
            self.check_post_conditions(exploration_model, app_home_states_all)

        return set(state.state_id for state in app_home_states_all)

    def tag_use_case_execution(self, use_case_execution, index: int):
        assert index > 0, f"Index was: {index}"
        traces = use_case_execution.get_playback_traces()
        assert traces, f"Trace size was: {len(traces)}"
        for trace in traces:
            # Always use the source state
            state_id = trace.transitions[index].source_state_o.unique_id
            trace.app_home_state = state_id

    def check_post_conditions(self, exploration_model, app_home_states: Set[StateWrapper]):
        assert app_home_states, f"app_home_states was {app_home_states}"

        # Every use case execution should have a tagged app home state
        for uce in filter(lambda uce: uce.is_verified(), exploration_model.use_case_execution_manager.use_case_executions):
            uce_trace = uce.get_representative_trace()
            assert uce_trace.app_home_state is not None and uce_trace.app_home_state != ""

        # Don't tag the home screen!
        assert all(not tagged_state.is_home_screen() for tagged_state in app_home_states)
