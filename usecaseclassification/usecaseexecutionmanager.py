# -*- coding: utf-8 -*-
import os
import pickle
from dataclasses import dataclass
from typing import List, Iterable, Tuple

from model.tagger.ucestarttagger import UCEStartTagger
from model.usecase import UseCase
from model.usecaseexecutionexplorationmodel import UseCaseExecutionExplorationModel
from usecaseclassification.dummyusecaseexecution import DummyUseCaseExecution
from usecaseclassification.usecaseexecution import UseCaseExecution
from util import configutil
from util.modelutil import get_csv_dict_reader


SUCCESS = "SUCCESS"
FAIL = "FAIL"


@dataclass
class ResultsState:
    state: str
    trace_id: str
    playback_idx: int


class UseCaseExecutionManager(object):
    def __init__(self, exploration_model):
        self.exploration_model = exploration_model
        self.use_case_executions: List[UseCaseExecution] = []
        self.use_case_execution_use_case_name_map = {}

    @staticmethod
    def load_from_cache(exploration_model):
        file_executions = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, f"usecaseexecutionmanager_{exploration_model.package_name}_use_case_executions")
        assert os.path.isfile(file_executions), f"File does not exist: {file_executions}"
        with open(file_executions, 'rb') as fp:
            use_case_executions = pickle.load(fp)
        assert use_case_executions is not None

        file_map = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, f"usecaseexecutionmanager_{exploration_model.package_name}_use_case_execution_use_case_name_map")
        assert os.path.isfile(file_map), f"File does not exist: {file_map}"
        with open(file_map, 'rb') as fp:
            use_case_execution_use_case_name_map = pickle.load(fp)
        assert use_case_execution_use_case_name_map is not None

        uce_manager = UseCaseExecutionManager(exploration_model)
        uce_manager.use_case_executions = use_case_executions
        uce_manager.use_case_execution_use_case_name_map = use_case_execution_use_case_name_map

        return uce_manager

    def store_data(self):
        file_executions = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, f"usecaseexecutionmanager_{self.exploration_model.package_name}_use_case_executions")
        with open(file_executions, 'wb') as f:
            local_use_case_executions = [DummyUseCaseExecution.construct_from_use_case_execution(uce)
                                         for uce in self.use_case_executions]
            pickle.dump(local_use_case_executions, f)

        file_map = os.path.join(configutil.MATRICS_CACHE_DIR_NAME, f"usecaseexecutionmanager_{self.exploration_model.package_name}_use_case_execution_use_case_name_map")
        with open(file_map, 'wb') as f:
            local_use_case_execution_use_case_name_map = {k: DummyUseCaseExecution.construct_from_use_case_execution(uce)
                                                          for k, uce in self.use_case_execution_use_case_name_map.items()}
            pickle.dump(local_use_case_execution_use_case_name_map, f)

    def add_use_case_execution(self, use_case_execution: UseCaseExecution):
        self.use_case_executions.append(use_case_execution)
        self.use_case_execution_use_case_name_map[use_case_execution.use_case.name] = use_case_execution

    def add_all_use_case_executions(self, use_case_execution: Iterable[UseCaseExecution]):
        for uce in use_case_execution:
            self.add_use_case_execution(uce)

    def get_use_case_execution(self, use_case: UseCase):
        if use_case.name in self.use_case_execution_use_case_name_map:
            return self.use_case_execution_use_case_name_map[use_case.name]
        else:
            use_case_execution = UseCaseExecution(use_case=use_case, computed=False, computed_paths=[])
            self.add_use_case_execution(use_case_execution)
            return use_case_execution
        # uce = next((uce for uce in self.use_case_executions if uce.use_case == use_case), default=None)
        # if uce is None:
        #     uce = UseCaseExecution(use_case=use_case, computed_paths=[])
        # return uce

    def has_use_case(self, use_case: UseCase, ignore_playback_state=False):
        uce = self.use_case_execution_use_case_name_map[use_case.name] if use_case.name in self.use_case_execution_use_case_name_map else None
        if uce is None:
            return False
        else:
            return ignore_playback_state or uce.playback_state == SUCCESS

    def get_computed_use_case_executions(self) -> List[UseCaseExecution]:
        return [use_case_execution
                for use_case_execution in self.use_case_executions
                if use_case_execution.computed]

    def get_verified_use_case_executions(self) -> List[UseCaseExecution]:
        return [use_case_execution
                for use_case_execution in self.use_case_executions
                if use_case_execution.playback_state == SUCCESS]

    def get_use_case_executions(self, filter_not_successful=False) -> List[UseCaseExecution]:
        # TODO filter_not_successful
        return [use_case_execution
                for use_case_execution in self.use_case_executions
                if use_case_execution.is_computed() or use_case_execution.is_verified()]

    def read_exploration_models(self, require_existence):
        """
        ./Data/run/exploration/playback1
        """
        package_name = self.exploration_model.package_name
        parent_exploration_dir = os.path.dirname(os.path.dirname(os.path.dirname(self.exploration_model.exploration_model_dir)))

        # Read the playback results csv files to know the status and trace id
        use_case_name_results_state_map = self.read_playback_results(self.exploration_model.matrics_playback_dir, package_name)
        use_case_names = set([ucname for ucname in self.use_case_execution_use_case_name_map] + [ucname for ucname in use_case_name_results_state_map])

        for use_case_name in use_case_names:
            if use_case_name in use_case_name_results_state_map:
                playback_result = use_case_name_results_state_map[use_case_name]
            else:
                # The use case might be removed for the execution because it was not successful
                playback_result = ResultsState(FAIL, None, None)
            if use_case_name in self.use_case_execution_use_case_name_map:
                use_case_execution = self.use_case_execution_use_case_name_map[use_case_name]
            else:
                assert not require_existence, f"Use case '{use_case_name}' was not computed before"
                # The use case execution might not be constructed before, because the computation was disabled
                # TODO not very optimal
                use_case = UseCase(name=use_case_name)
                use_case_execution = self.get_use_case_execution(use_case)
            use_case_execution.playback_state = playback_result.state
            use_case_execution.playback_index = playback_result.playback_idx
            use_case_execution.playback_trace_id = playback_result.trace_id

        # Read the actual execution/exploration
        self.read_playback_models(parent_exploration_dir, package_name)

        self.check_post_conditions()

    def read_playback_results(self, matrics_playback_dir, package_name):
        use_case_name_results_state_map = {}
        playback_model_dir = os.path.join(matrics_playback_dir, configutil.TOGAPE_MODEL_DIR_NAME, package_name)
        playback_result_files = sorted([os.path.join(playback_model_dir, f)
                                        for f in os.listdir(playback_model_dir)
                                        if f.startswith(configutil.PLAYBACK_RESULTS_CSV_PREFIX) and f.endswith(".csv")])
        # Can only assert > 0, there are also failed playbacks
        assert len(playback_result_files) > 0, f"Size of playback_result_files was {len(playback_result_files)}"
        with open(playback_result_files[0], newline='') as f:
            csvreader = get_csv_dict_reader(f)
            for row in csvreader:
                use_case_name = row["Use Case Name"]
                use_case_name = str(use_case_name).strip().replace(" ", "_")
                # Search for the first successful execution if existent
                playback_result = ResultsState(FAIL, None, None)
                for i in range(configutil.MATRICS_NUMBER_OF_PATH_SELECTION):
                    results_state_str = row[f"Playback{i} State"]
                    if results_state_str == SUCCESS:
                        results_trace_id = row[f"Playback{i} trace id"]
                        playback_result = ResultsState(results_state_str, results_trace_id, i)
                        break

                use_case_name_results_state_map[use_case_name] = playback_result

        return use_case_name_results_state_map

    def read_playback_models(self, parent_exploration_dir, package_name):
        corresponding_use_case_executions = [uce for uce in self.use_case_executions if uce.playback_trace_id is not None]
        for i in range(1, configutil.MATRICS_PLAYBACK_ITERATION_NUMBER + 1):
            model_dir = os.path.join(parent_exploration_dir,
                                     f"playback{i}",
                                     configutil.TOGAPE_MODEL_DIR_NAME,
                                     package_name)
            feauture_dir = os.path.join(model_dir, configutil.TOGAPE_FEATURE_DIR_NAME)
            use_case_execution_exploration_model = UseCaseExecutionExplorationModel(app=None,
                                                                                    package_name=package_name,
                                                                                    exploration_model_dir=model_dir,
                                                                                    feature_dir=feauture_dir,
                                                                                    evaluation_dir=None)

            for uce in corresponding_use_case_executions:
                uce.playback_exploration_models.append(use_case_execution_exploration_model)

    def check_post_conditions(self):
        for uce in self.get_verified_use_case_executions():
            assert uce.playback_state == SUCCESS
            assert len(uce.playback_exploration_models) == configutil.MATRICS_PLAYBACK_ITERATION_NUMBER
            assert len(uce.get_playback_traces()) == configutil.MATRICS_PLAYBACK_ITERATION_NUMBER, \
                f"Use Case Execution '{uce.use_case.name}' Size playback traces: {len(uce.get_playback_traces())} Expected: {configutil.MATRICS_PLAYBACK_ITERATION_NUMBER}"
            uce.get_representative_trace()

            assert len(set(len(trace.transitions) for trace in uce.get_playback_traces())) == 1, \
                f"Different trace lengths: {[len(trace.transitions) for trace in uce.get_playback_traces()]}"

    def tag_uce_start(self):
        tagger = UCEStartTagger()
        tagger.tag_states(self.exploration_model)

    def get_playback_statistics(self) -> Tuple[int, int]:
        matrics_playback_dir = self.exploration_model.matrics_playback_dir
        package_name = self.exploration_model.package_name
        playback_model_dir = os.path.join(matrics_playback_dir, configutil.TOGAPE_MODEL_DIR_NAME, package_name)
        playback_result_files = sorted([os.path.join(playback_model_dir, f)
                                        for f in os.listdir(playback_model_dir)
                                        if f.startswith(configutil.PLAYBACK_RESULTS_CSV_PREFIX) and f.endswith(".csv")])
        # Can only assert > 0, there are also failed playbacks
        assert len(playback_result_files) > 0, f"Size of playback_result_files was {len(playback_result_files)}"

        failed_playbacks = []
        successful_playbacks = []

        with open(playback_result_files[0], newline='') as f:
            csvreader = get_csv_dict_reader(f)
            for row in csvreader:
                use_case_name = row["Use Case Name"]
                use_case_name = str(use_case_name).strip().replace(" ", "_")
                # Search for the first successful execution if existent
                for i in range(configutil.MATRICS_NUMBER_OF_PATH_SELECTION):
                    results_state_str = row[f"Playback{i} State"]
                    if results_state_str == SUCCESS:
                        successful_playbacks.append(f"{use_case_name}_{i}")
                        break
                    elif results_state_str == FAIL:
                        failed_playbacks.append(f"{use_case_name}_{i}")

        return len(successful_playbacks), len(failed_playbacks)
