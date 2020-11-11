# -*- coding: utf-8 -*-
import os

from model.explorationmodel import ExplorationModel
from usecaseclassification.processor.transitionusecaseexclusioncriterion import TransitionUseCaseExclusionCriterion
from usecaseclassification.processor.usecasepathexclusioncriterion import UseCasePathExclusionCriterion
from usecaseclassification.usecaseexecutionmanager import UseCaseExecutionManager
from visualization import graphviz
from util import configutil
from visualization.visdccusecaseexecutionsviz import VisdccUseCaseExecutionsViz


class DummyExplorationModel(object):
    def __init__(self,
                 app,
                 package_name,
                 exploration_model_dir,
                 feature_dir,
                 evaluation_dir,
                 use_case_manager,
                 matrics_playback_dir,
                 compute_use_case_executions_b: bool):
        self.package_name = package_name
        self.exploration_model_dir = exploration_model_dir
        self.states_dir = os.path.join(self.exploration_model_dir, configutil.TOGAPE_MODEL_STATES_DIR_NAME)
        self.uid_state_map = {}
        self.uid_widget_map = {}
        self.uid_trace_map = {}
        self.actionid_transition_map = {}

        self.states = []
        # Single home state. We try to identify the correct home state from the exploration, because multiple home
        # states screw up our path search.
        self.home_state = None
        self.traces = []
        self.image_paths = {}

        # Network
        self.hars = []

        self.use_case_manager = use_case_manager
        self.matrics_playback_dir = matrics_playback_dir
        self.compute_use_case_executions_b: bool = compute_use_case_executions_b
        # self.read_atds(feature_dir)
        # self.overall_graph: graph.Graph = self.create_graph()

        # Use case related model properties
        self.transition_use_case_exclusion_criterion = TransitionUseCaseExclusionCriterion(self)
        self.use_case_path_exclusion_criterion = UseCasePathExclusionCriterion()
        # self.use_case_base_unmodified_graph: graph.Graph = self.create_graph(exclusion_criterion=self.transition_use_case_exclusion_criterion)
        # self.use_case_base_transformed_graph: graph.Graph = self.create_graph(exclusion_criterion=self.transition_use_case_exclusion_criterion)
        # self.use_case_base_graph = self.use_case_base_transformed_graph

        # self.use_case_processor = UseCaseProcessorInteractionSelection(self)
        self.use_case_execution_manager = self.get_use_case_execution_manager()

        # Lazy loading
        self.viz_overall_graph = None
        self.viz_use_case_base_graph = None
        self.viz_use_case_base_unmodified_graph = None
        self.viz_use_case_base_transformed_graph = None
        self.viz_use_case_exec_graphs = None

    @staticmethod
    def create_from_exploration_model(exploration_model: ExplorationModel):
        return DummyExplorationModel.create(app=exploration_model.app,
                                            package_name=exploration_model.package_name,
                                            exploration_model_dir=exploration_model.exploration_model_dir,
                                            use_case_manager=exploration_model.use_case_manager,
                                            matrics_playback_dir=exploration_model.matrics_playback_dir,
                                            compute_use_case_executions_b=exploration_model.compute_use_case_executions_b)

    @staticmethod
    def create(app, package_name, exploration_model_dir, use_case_manager, matrics_playback_dir, compute_use_case_executions_b):
        return DummyExplorationModel(app=app,
                                     package_name=package_name,
                                     exploration_model_dir=exploration_model_dir,
                                     feature_dir="",
                                     evaluation_dir="",
                                     use_case_manager=use_case_manager,
                                     matrics_playback_dir=matrics_playback_dir,
                                     compute_use_case_executions_b=compute_use_case_executions_b)

    def get_use_case_execution_manager(self):
        use_case_execution_manager = None
        if configutil.MATRICS_CACHE_READ:
            use_case_execution_manager = UseCaseExecutionManager.load_from_cache(self)
        else:
            use_case_execution_manager = UseCaseExecutionManager(self)
        return use_case_execution_manager

    def node_info(self, node):
        return ""

    def edges_info(self, edges):
        return ""

    def plot_use_case_base_graph(self):
        """
        Return the visualized graph used for the use case calculations.

        Default graph, depends on use_case_base_graph.
        """
        self.viz_use_case_base_graph = graphviz.VisdccUseCaseBaseDefaultGraphViz(self.use_case_base_graph) if self.viz_use_case_base_graph is None else self.viz_use_case_base_graph
        return self.viz_use_case_base_graph.visualize_graph()

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
        self.viz_use_case_exec_graphs = VisdccUseCaseExecutionsViz(self, False) if self.viz_use_case_exec_graphs is None else self.viz_use_case_exec_graphs
        # self.viz_use_case_exec_graphs = VisdccMultipleUseCaseExecutionsViz(self) if self.viz_use_case_exec_graphs is None else self.viz_use_case_exec_graphs
        return self.viz_use_case_exec_graphs.visualize_graph()

    def plot(self):
        """
        Return the visualization of the overall graph with all states and transitions.
        """
        self.viz_overall_graph = graphviz.VisdccOverallGraphViz(self.overall_graph) if self.viz_overall_graph is None else self.viz_overall_graph
        return self.viz_overall_graph.visualize_graph()
