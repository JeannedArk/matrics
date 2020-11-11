# -*- coding: utf-8 -*-
from typing import List, Optional

from graph.path import Path
from model.baseexplorationmodel import BaseExplorationModel
from model.trace import Trace
from model.usecase import UseCase
from model.view import View
from util import configutil


class UseCaseExecution(object):
    def __init__(self, use_case: UseCase, computed: bool, computed_paths: List[Path]):
        self.use_case = use_case
        self.computed: bool = computed

        # Paths must be empty if the use case execution is not computed
        assert computed or (not computed and not computed_paths)
        # Process paths
        computed_paths.sort()
        for path in computed_paths:
            assert path.nodes, "Expected the length of the path greater than 0"
            assert len(path.nodes) >= path.actual_length, "Path invariance"
        self.computed_paths = computed_paths

        # Trace id that is used for the playback, set when the playback dir is processed
        self.playback_trace_id: Optional[str] = None
        self.playback_state: Optional[str] = None
        self.playback_index: Optional[int] = None
        self.start_index: Optional[int] = None
        self.playback_exploration_models: List[BaseExplorationModel] = []
        self.view: Optional[View] = None

    def __eq__(self, o: object) -> bool:
        """
        Equality is defined as the equality of the use case name.
        This is used for some metrics.
        """
        raise RuntimeError("TODO")
        # if isinstance(o, UseCaseExecution):
        #     return self.use_case.name == o.use_case.name
        # else:
        #     return False

    def __hash__(self) -> int:
        """
        Needed to be hashable in dicts for the visualization graphs.
        """
        return id(self)

    def init_view(self) -> None:
        self.view = View(self)

    def is_computed(self) -> bool:
        return self.computed

    def is_verified(self) -> bool:
        return len(self.get_playback_traces()) > 0

    def get_best_computed_path(self) -> Path:
        return self.computed_paths[0]

    def get_verified_computed_path(self) -> Path:
        """
        Return the computed path, that has been successfully verified. Use the corresponding playback index for that.
        """
        assert self.computed, f"Expected to be computed: {self.computed}"
        assert self.playback_index is not None, f"Playback index was {self.playback_index}"
        return self.computed_paths[self.playback_index]

    def get_computed_paths_selection(self) -> List[Path]:
        return self.computed_paths[:configutil.MATRICS_NUMBER_OF_PATH_SELECTION]

    def get_playback_traces(self) -> List[Trace]:
        return [trace
                for exploration_model in self.playback_exploration_models
                for trace in exploration_model.traces
                if trace.unique_id == self.playback_trace_id]

    def get_representative_trace_view(self) -> View:
        assert self.view is not None
        return self.view

    def get_representative_trace(self) -> Trace:
        """
        TODO right now only returning first trace
        """
        return self.get_playback_traces()[0]

    def get_representative_exploration_model(self) -> BaseExplorationModel:
        """
        TODO right now only returning first exploration model
        """
        return self.playback_exploration_models[0]
