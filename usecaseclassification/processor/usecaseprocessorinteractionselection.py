# -*- coding: utf-8 -*-
import collections
import itertools
from typing import List

from tqdm import tqdm

import usecasemapping
from graph.multinodepathsolver import MultiNodePathSolver
from criterion.basecriterion import BaseCriterion
from usecaseclassification.processor.usecaseprocessor import UseCaseProcessor
from usecaseclassification.usecaseexecution import UseCaseExecution
from usecaseclassification.usecasereader import UseCaseReader


MAX_COMBINATIONS = 500


def soft_string_equal(s1: str, s2: str):
    return s1.lower().strip() == s2.lower().strip()


class ATDBasedTransitionSelectCriterion(BaseCriterion):

    SIMILARITY_THRESHOLD = 0.5

    def __init__(self, exploration_model):
        self.exploration_model = exploration_model

    def decide(self, trans, atd):
        # filtered_features = [atd_record.atd.target_descriptor
        #                      for atd_record in state.atd_records
        #                      if atd_record.widget_o is not None and atd_record.widget_o.is_interactable_and_visible()
        #                      # if atd_record.widget_o.is_interactable_and_visible()
        atd_records = list(
            filter(lambda atd_r: atd_r.atd == atd
                                 and atd_r.widget_o == trans.interacted_widget_o
                                 and atd_r.similarity >= ATDBasedTransitionSelectCriterion.SIMILARITY_THRESHOLD
                                 and atd_r.atd.action_type.value == trans.action
                   , trans.source_state_o.atd_records))
        # assert trans.source_state_o == trans.interacted_widget_o.source_state_o

        return len(atd_records) > 0


class UseCaseProcessorInteractionSelection(UseCaseProcessor):
    def __init__(self, exploration_model, filter_use_cases=True):
        self.exploration_model = exploration_model
        self.filter_use_cases = filter_use_cases
        self.use_cases, self.unassigned_atds, self.feature_use_cases_map = self.exploration_model.use_case_manager.get_use_case_data()
        self.atd_based_transition_select_criterion = ATDBasedTransitionSelectCriterion(self.exploration_model)
        self.use_case_path_exclusion_criterion = self.exploration_model.use_case_path_exclusion_criterion
        self.path_finder = MultiNodePathSolver(self.exploration_model, self.use_case_path_exclusion_criterion)

    def compute_use_case_executions(self) -> List[UseCaseExecution]:
        """
        TODO think about a criterion that finally decides to use this generated use case
        e.g. TwitterLite trace404599ab-fc26-4388-9f47-6a0563000003.csv
        there is only a close interaction.
        """
        possible_use_case_executions = []
        home_state = self.exploration_model.home_state.unique_id

        use_cases = []
        if self.filter_use_cases:
            assert self.exploration_model.package_name in usecasemapping.APP_USE_CASE_MAP,\
                f"{self.exploration_model.package_name} was not in APP_USE_CASE_MAP"
            allowed_use_cases = usecasemapping.APP_USE_CASE_MAP[self.exploration_model.package_name]
            use_cases = filter(
                lambda uc: any(soft_string_equal(uc.name, uc_name_allowed) for uc_name_allowed in allowed_use_cases),
                self.use_cases)
        else:
            use_cases = self.use_cases

        for use_case in tqdm(use_cases, desc="Use cases"):

            # Identify states that include the desired feature for the use case
            atd_transitions_list_map = collections.defaultdict(list)

            for atd in use_case.atds_flatted:
                # Transitions that include the desired atd
                transitions_w_atd = [(trans, atd)
                                     for trans in self.exploration_model.use_case_base_graph.transitions
                                     if self.atd_based_transition_select_criterion.decide(trans, atd)]
                if transitions_w_atd:
                    atd_transitions_list_map[atd] = transitions_w_atd

            # For every combination of transitions regarding the atd
            paths = []
            if atd_transitions_list_map.values():
                # print(f"len(atd_transitions_list_map.values()) {len(atd_transitions_list_map.values())}")
                transition_combinations = UseCaseProcessor.get_combinations(atd_transitions_list_map)
                # print(f"Number of combinations: {len(list(transition_combinations))} Combinations to try: {len(transition_combinations[:MAX_COMBINATIONS])}")
                for transitions_w_atds_ls in itertools.islice(transition_combinations, 0, MAX_COMBINATIONS):
                    path = self.path_finder.find_path(transitions_w_atds_ls, home_state)
                    if path is not None:
                        path = self.append_terminate(path=path,
                                                     uid_state_map=self.exploration_model.uid_state_map,
                                                     resulting_end_state=home_state)
                        # Create trace from path
                        path.construct_trace(exploration_model=self.exploration_model)
                        paths.append(path)
            if paths:
                use_case_exec = UseCaseExecution(use_case=use_case, computed=True, computed_paths=paths)
                possible_use_case_executions.append(use_case_exec)

        return possible_use_case_executions
