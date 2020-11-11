# -*- coding: utf-8 -*-
import json
import os
import pickle
from typing import Set

from graph import graph
from model.tagger.apphomestatetagger import AppHomeStateVerifiedUCETagger, AppHomeStateComputedUCETagger
from model.baseexplorationmodel import BaseExplorationModel
from model.tagger.apphomestatetagmanager import AppHomeStateTagManager
from usecaseclassification.processor.transitionusecaseexclusioncriterion import TransitionUseCaseExclusionCriterion
from usecaseclassification.processor.usecasepathexclusioncriterion import UseCasePathExclusionCriterion
from usecaseclassification.usecaseexecutionmanager import UseCaseExecutionManager
from visualization import graphviz
from usecaseclassification.processor.usecaseprocessorinteractionselection import UseCaseProcessorInteractionSelection
from util import configutil
from util.pathutil import create_dir_if_non_existing
from model.atd import ATD, ATDRecord
from visualization.visdccusecaseexecutionsviz import VisdccUseCaseExecutionsViz


EXPLORATION_MODEL_FILE_NAME = "exploration_model.matrics"
USE_CASE_EXECUTIONS_DIR_NAME = "usecaseexecutions"
USE_CASE_EXECUTIONS_FILE_NAME = "use_case_executions.matrics"
USE_CASE_TRACE_INFO_FILE_NAME = "use_case_trace_info.txt"


class ExplorationModel(BaseExplorationModel):
    """
    TODO does not log
    """

    def __init__(self,
                 app,
                 package_name,
                 exploration_model_dir,
                 feature_dir,
                 evaluation_dir,
                 use_case_manager,
                 matrics_playback_dir,
                 compute_use_case_executions_b: bool):
        super().__init__(app, package_name, exploration_model_dir, feature_dir, evaluation_dir)
        self.use_case_manager = use_case_manager
        self.matrics_playback_dir = matrics_playback_dir
        self.compute_use_case_executions_b: bool = compute_use_case_executions_b
        self.read_atds(feature_dir)
        self.overall_graph: graph.Graph = self.create_graph()
        self.app_home_state_tag_manager = AppHomeStateTagManager(self)

        # Use case related model properties
        self.transition_use_case_exclusion_criterion = TransitionUseCaseExclusionCriterion(self)
        self.use_case_path_exclusion_criterion = UseCasePathExclusionCriterion()
        self.use_case_base_unmodified_graph: graph.Graph = self.create_graph(exclusion_criterion=self.transition_use_case_exclusion_criterion)
        self.use_case_base_transformed_graph: graph.Graph = self.create_graph(exclusion_criterion=self.transition_use_case_exclusion_criterion)
        # self.use_case_base_unmodified_graph: graph.Graph = self.create_graph()
        # self.use_case_base_transformed_graph: graph.Graph = self.create_graph()
        self.use_case_base_transformed_graph.merge_graph()  # TODO
        self.use_case_base_graph: graph.Graph = self.use_case_base_transformed_graph

        self.use_case_processor = UseCaseProcessorInteractionSelection(self)
        self.use_case_execution_manager = UseCaseExecutionManager(self)
        # if False:
        if self.compute_use_case_executions_b:
            self.compute_use_case_executions()

        if configutil.MATRICS_TAG_APP_HOME_STATE:
            self.tag_app_home_state()
        self.finalize_use_case_executions()

        # Lazy loading
        self.viz_overall_graph = None
        self.viz_use_case_base_graph = None
        self.viz_use_case_base_w_app_home_states_graph = None
        self.viz_use_case_base_unmodified_graph = None
        self.viz_use_case_base_transformed_graph = None
        self.viz_use_case_exec_graphs = None

        self.check_post_conditions()

    @staticmethod
    def load_exploration_model(app,
                               package_name,
                               exploration_model_dir,
                               feature_dir,
                               evaluation_dir,
                               use_case_manager,
                               matrics_playback_dir,
                               compute_use_case_executions_b,
                               load_from_file=False):
        dump_f = os.path.join(exploration_model_dir, EXPLORATION_MODEL_FILE_NAME)
        exploration_model = None
        if load_from_file and os.path.isfile(dump_f):
            with open(dump_f, 'rb') as f:
                exploration_model = pickle.load(f)
        else:
            exploration_model = ExplorationModel(app=app,
                                                 package_name=package_name,
                                                 exploration_model_dir=exploration_model_dir,
                                                 feature_dir=feature_dir,
                                                 evaluation_dir=evaluation_dir,
                                                 use_case_manager=use_case_manager,
                                                 matrics_playback_dir=matrics_playback_dir,
                                                 compute_use_case_executions_b=compute_use_case_executions_b)
            # Enable dumping when we are able to pickle the data structures.
            # with open(dump_f, 'wb') as f:
            #     pickle.dump(exploration_model, f, pickle.HIGHEST_PROTOCOL)
        return exploration_model

    @staticmethod
    def convert_to_atds(atd_records_d, uid_widget_map):
        atd_records = []
        for atd_rec_d in atd_records_d:
            atd = ATD(atd_rec_d['atd']['actionType'], atd_rec_d['atd']['targetDescriptor'], atd_rec_d['atd']['data'])
            widget_string = atd_rec_d['widgetString']
            assert widget_string[0] == '"' and ";" in widget_string

            # TODO check this and create a comment
            # wid = (widget_string.partition(";")[0])[1:]
            # if atd_rec_d['idOfLabelW'] == "null":
            #     wid = (widget_string.partition(";")[0])[1:]
            # else:
            #     wid = atd_rec_d['idOfLabelW']
            wid = (widget_string.partition(";")[0])[1:]
            # NOT TRUE We don't create the wid from the widget_string anymore
            # assert wid in uid_widget_map, f"Expected widget id {uid_widget_map} to be present in uid_widget_map"
            if wid in uid_widget_map:
                widget = uid_widget_map[wid]
            else:
                widget = None

            atd_rec = ATDRecord(atd=atd,
                                label_text=atd_rec_d['labelText'],
                                similarity=atd_rec_d['similarity'],
                                weight=atd_rec_d['weight'],
                                parent_id=atd_rec_d['parentId'],
                                id_of_label_w=wid,
                                id_of_label_w_orig=atd_rec_d['idOfLabelW'],
                                label_dist=atd_rec_d['labelDist'],
                                widget_string=atd_rec_d['widgetString'],
                                widget_o=widget)
            atd_records.append(atd_rec)

        return atd_records

    def read_atds(self, feature_dir):
        num_atd_files = 0
        for f_name in os.listdir(feature_dir):
            f = os.path.join(feature_dir, f_name)
            if os.path.isfile(f) and f_name.startswith(f"ATD-R_"):
                for t in self.traces:
                    if f_name == f"ATD-R_{self.package_name}-{t.unique_id}.json":
                        print(f"Found atd file: {f}")
                        num_atd_files += 1
                        with open(f) as json_file:
                            data = json.load(json_file)
                            assert data['appName'] == self.package_name
                            assert data['traceId'] == t.unique_id
                            state_ATDs = data['stateATDs']
                            for s_id in state_ATDs:
                                s = self.uid_state_map[s_id]
                                s.process_atd_records(ExplorationModel.convert_to_atds(state_ATDs[s_id], self.uid_widget_map))
                                s.draw_ATDs_on_img()
        assert num_atd_files == len(self.traces), f"Unexpected number of found atd files = {num_atd_files} num traces: {len(self.traces)}"

    def tag_app_home_state(self):
        app_home_states = self.app_home_state_tag_manager.get_app_home_states()
        app_home_states_in_base_graph = [self.uid_state_map[app_home_state]
                                         for app_home_state in app_home_states
                                         if app_home_state in self.uid_state_map]
        self.use_case_base_graph.add_app_home_states(app_home_states_in_base_graph)

    def compute_use_case_executions(self, dump_computed_use_case_execution_models=False) -> None:
        # try:
            use_case_executions = self.use_case_processor.compute_use_case_executions()
            self.use_case_execution_manager.add_all_use_case_executions(use_case_executions)

            if dump_computed_use_case_execution_models:
                target_exploration_model_dir = os.path.join(self.matrics_playback_dir,
                                                            configutil.TOGAPE_MODEL_DIR_NAME,
                                                            self.package_name)
                self.dump_use_case_executions_model(target_model_dir=target_exploration_model_dir)

            # Read in use case executions
            self.use_case_execution_manager.read_exploration_models(require_existence=True)
            self.use_case_execution_manager.tag_uce_start()
            self.use_case_execution_manager.store_data()
        # except Exception as e:
        #     raise RuntimeError(f"Exception for {self.package_name}: {e} {e.__class__} {e.args}")

    def finalize_use_case_executions(self):
        # Initialize the use case execution's view, because the states were tagged
        for uce in self.use_case_execution_manager.get_verified_use_case_executions():
            uce.init_view()

    def dump_states(self, graph, target_states_dir):
        # if not os.path.isdir(target_states_dir):
        #     shutil.copytree(self.states_dir, target_states_dir)
        create_dir_if_non_existing(target_states_dir)
        for state in graph.states:
            state.dump_to_file(target_states_dir)

    def dump_use_case_executions_model(self, target_model_dir):
        """
        Dump the model with use case executions traces for the DM2 playback.
        """
        # Copy the states data
        create_dir_if_non_existing(target_model_dir)
        target_states_dir = os.path.join(target_model_dir, configutil.TOGAPE_MODEL_STATES_DIR_NAME)
        # if not os.path.isdir(target_states_dir):
        #     shutil.copytree(self.states_dir, target_states_dir)
        self.dump_states(self.use_case_base_graph, target_states_dir)

        # Dump the computed traces
        for use_case_exec in self.use_case_execution_manager.use_case_executions:
            # Create a dedicated directory for the trace candidates
            use_case_exec_dir = os.path.join(target_model_dir, f"{use_case_exec.use_case.name}")
            create_dir_if_non_existing(use_case_exec_dir)

            # Create a file with the id mapping
            trace_use_case_map_file = os.path.join(use_case_exec_dir, USE_CASE_TRACE_INFO_FILE_NAME)
            use_case_exec_paths: list = use_case_exec.get_computed_paths_selection()
            for i, use_case_exec_path in enumerate(use_case_exec_paths):
                trace = use_case_exec_path.trace
                trace.idx = i
                # Assign a new unique trace id
                trace.generate_trace_id(use_case_exec.use_case)
                # Dump the trace file
                trace.dump_to_file(target_dir=use_case_exec_dir)

                write_mode = 'a' if os.path.exists(trace_use_case_map_file) else 'w'
                with open(trace_use_case_map_file, mode=write_mode) as f:
                    f.write(f"====================================================================================\n{trace.unique_id}\n")
                    f.write(f"{use_case_exec.use_case.to_string_short()} :\n{trace}\n\n\n")

    def node_info(self, node):
        """
        This is really ugly, could be refactored.
        """
        state = self.get_state_from_uid(node)
        if self.viz_overall_graph is not None:
            return self.viz_overall_graph.node_info(state)
        elif self.viz_use_case_base_graph is not None:
            return self.viz_use_case_base_graph.node_info(state)
        else:
            return self.viz_use_case_base_transformed_graph.node_info(state)

    def edges_info(self, edges):
        """
        This is really ugly, could be refactored.
        """
        if self.viz_overall_graph is not None:
            return self.viz_overall_graph.edges_info(edges)
        elif self.viz_use_case_base_graph is not None:
            return self.viz_use_case_base_graph.edges_info(edges)
        else:
            return self.viz_use_case_base_transformed_graph.edges_info(edges)

    def plot_use_case_base_graph(self):
        """
        Return the visualized graph used for the use case calculations.

        Default graph, depends on use_case_base_graph.
        """
        self.viz_use_case_base_graph = graphviz.VisdccUseCaseBaseDefaultGraphViz(self.use_case_base_graph, mark_app_home_states=False) \
            if self.viz_use_case_base_graph is None\
            else self.viz_use_case_base_graph
        return self.viz_use_case_base_graph.visualize_graph()

    def plot_app_home_state_graph(self):
        self.viz_use_case_base_w_app_home_states_graph = graphviz.VisdccUseCaseBaseDefaultGraphViz(self.use_case_base_graph, mark_app_home_states=True) \
            if self.viz_use_case_base_w_app_home_states_graph is None\
            else self.viz_use_case_base_w_app_home_states_graph
        return self.viz_use_case_base_w_app_home_states_graph.visualize_graph()

    def plot_use_case_base_unmodified_graph(self):
        self.viz_use_case_base_unmodified_graph = graphviz.VisdccUseCaseBaseUnmodifiedGraphViz(self.use_case_base_unmodified_graph) if self.viz_use_case_base_unmodified_graph is None else self.viz_use_case_base_unmodified_graph
        return self.viz_use_case_base_unmodified_graph.visualize_graph()

    def plot_use_case_base_transformed_graph(self):
        """
        Return the visualized graph used for the use case calculations.
        """
        self.viz_use_case_base_transformed_graph = graphviz.VisdccUseCaseBaseTransformedGraphViz(self.use_case_base_transformed_graph) if self.viz_use_case_base_transformed_graph is None else self.viz_use_case_base_transformed_graph
        return self.viz_use_case_base_transformed_graph.visualize_graph()

    def plot_use_case_executions(self):
        """
        Return the visualized use case executions.
        """
        self.viz_use_case_exec_graphs = VisdccUseCaseExecutionsViz(self, mark_app_home_states=True)\
            if self.viz_use_case_exec_graphs is None\
            else self.viz_use_case_exec_graphs
        # self.viz_use_case_exec_graphs = VisdccMultipleUseCaseExecutionsViz(self) if self.viz_use_case_exec_graphs is None else self.viz_use_case_exec_graphs
        return self.viz_use_case_exec_graphs.visualize_graph()

    def plot(self):
        """
        Return the visualization of the overall graph with all states and transitions.
        """
        self.viz_overall_graph = graphviz.VisdccOverallGraphViz(self.overall_graph) if self.viz_overall_graph is None else self.viz_overall_graph
        return self.viz_overall_graph.visualize_graph()
