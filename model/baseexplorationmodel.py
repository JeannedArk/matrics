# -*- coding: utf-8 -*-
import logging
import os
from abc import ABCMeta

from datatypes.orderedset import OrderedSet
from graph import graph
from model.har import Har
from model.state import State
from model.trace import Trace
from util import configutil
from util.configutil import ATD_IMG_SUBDIR, RESIZE_IMG_SUBDIR
from util.pathutil import create_dir_if_non_existing


HOME_SCREEN_FILE_SUFFIX = "_HS"
IMAGE_FILE_EXTENSION = ".jpg"

# This can take a lot of time
FORCE_REDRAWING = False

# FORCE_REDUMP_USE_CASE_EXECUTIONS = False  # TODO be careful
FORCE_REDUMP_USE_CASE_EXECUTIONS = True  # TODO be careful
EXPLORATION_MODEL_FILE_NAME = "exploration_model.matrics"
USE_CASE_EXECUTIONS_DIR_NAME = "usecaseexecutions"
USE_CASE_EXECUTIONS_FILE_NAME = "use_case_executions.matrics"
USE_CASE_TRACE_INFO_FILE_NAME = "use_case_trace_info.txt"


class BaseExplorationModel(metaclass=ABCMeta):
    """
    TODO does not log
    """

    def __init__(self, app, package_name, exploration_model_dir, feature_dir, evaluation_dir):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('Model')
        print(f"Build model from: {exploration_model_dir}")
        # self.logger.info(f"Build model from: {exploration_model_dir}")
        self.app = app
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

        # Build the model
        self.read_states()
        self.read_traces(exploration_model_dir)
        self.read_images(feature_dir)

        # Network
        self.hars = []
        self.read_har_network(exploration_model_dir)

    def check_post_conditions(self):
        for trace in self.traces:
            for trans in trace.transitions:
                if trans.network_page is not None:
                    assert str(trans.network_page.actionIdx) == trans.action_id,\
                        f"Trans action_id: {trans.action_id} Trans network page actionIdx: {trans.network_page.actionIdx}"

    def read_states(self):
        for f_name in os.listdir(self.states_dir):
            state_file = os.path.join(self.states_dir, f_name)
            if os.path.isfile(state_file) and f_name.endswith(".csv"):
                self.logger.info(f"Found state file: {state_file}")
                # print(f"Found state file: {state_file}")
                state = State.construct_from_state_file(state_file, self.uid_widget_map)
                self.uid_state_map[state.unique_id] = state
                # Add to states
                self.states.append(state)
                if state.is_home_screen:
                    # Validate the home state
                    self.set_home_state(state)
        assert self.home_state is not None

    def read_traces(self, model_dir):
        for f_name in os.listdir(model_dir):
            trace_file = os.path.join(model_dir, f_name)
            if os.path.isfile(trace_file) and f_name.startswith("trace") and f_name.endswith(".csv"):
                self.logger.info(f"Found trace file: {trace_file}")
                trace = Trace.construct_from_trace_file(trace_file,
                                                        self.uid_state_map,
                                                        self.uid_widget_map,
                                                        self.actionid_transition_map)
                self.uid_trace_map[trace.unique_id] = trace
                # Add to traces
                self.traces.append(trace)

    def read_images(self, feature_dir):
        for f_name in os.listdir(feature_dir):
            f = os.path.join(feature_dir, f_name)
            if os.path.isdir(f):
                create_dir_if_non_existing(os.path.join(f, RESIZE_IMG_SUBDIR))
                # Create already the directory containing the images with ATD drawing
                create_dir_if_non_existing(os.path.join(f, ATD_IMG_SUBDIR))
                for t in self.traces:
                    if f.endswith(f"{self.package_name}-images_{t.unique_id}"):
                        for img_f_name in os.listdir(f):
                            if img_f_name.endswith(IMAGE_FILE_EXTENSION):
                                self.logger.info(f"Found img file: {img_f_name}")
                                actionId = img_f_name.replace(IMAGE_FILE_EXTENSION, "")
                                # print(f"Found img file: {img_f_name} id: {id}")
                                img_f = os.path.abspath(os.path.join(f, img_f_name))
                                self.image_paths[actionId] = img_f

                # Assign available images
                for actionId in self.actionid_transition_map:
                    if actionId in self.image_paths:
                        trans = self.actionid_transition_map[actionId]
                        s = trans.resulting_state_o
                        # TODO this assertion does not always hold
                        # probably create a set with (action_id, image)
                        # assert s.image_path is None or s.image_path == self.images[aid]
                        s.add_image_path(self.image_paths[actionId])

    def read_har_network(self, model_dir):
        for trace in self.traces:
            file_name = f"data{trace.unique_id}.har"
            file_path = os.path.join(model_dir, file_name)
            har = Har(file_path, self.uid_trace_map)
            self.hars.append(har)
            for page in har.pages:
                if page.actionIdx != -1:
                    actionIdx_s = str(page.actionIdx)
                    assert actionIdx_s in self.actionid_transition_map, f"{actionIdx_s} was not in actionid_transition_map"
                    transition = self.actionid_transition_map[actionIdx_s]
                    assert str(transition.action_id) == actionIdx_s, \
                        f"Expected action ids to match transition: {transition.action_id}  page: {page.actionIdx}"
                    transition.network_page = page

    def set_home_state(self, state):
        assert state.is_home_screen
        if not state.atd_records and not state.widgets:
            assert self.home_state is None
            self.home_state = state

    def get_state_from_uid(self, uid):
        return self.uid_state_map[uid]

    def create_graph(self, exclusion_criterion=None):
        states = OrderedSet()
        transitions = []

        for trace in self.traces:
            for trans in trace.transitions:
                if exclusion_criterion is None or not exclusion_criterion.decide(trans):
                    transitions.append(trans)

        # TODO maybe add only states that belong to a permitted transition
        for state in self.states:
            states.add(state)

        return graph.Graph(package_name=self.package_name,
                           states=states,
                           transitions=transitions,
                           home_state=self.home_state)
