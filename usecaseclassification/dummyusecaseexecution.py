# -*- coding: utf-8 -*-
from typing import List

from graph.path import Path
from model.baseexplorationmodel import BaseExplorationModel
from model.trace import Trace
from model.usecase import UseCase
from model.view import View
from util import configutil


class DummyUseCaseExecution(object):
    def __init__(self,
                 use_case: UseCase,
                 computed: bool,
                 verified: bool,
                 # computed_paths: List[Path],
                 playback_trace_id: str,
                 playback_state: str):
        self.use_case = use_case
        self.computed: bool = computed
        # self.computed_paths = computed_paths

        # Trace id that is used for the playback, set when the playback dir is processed
        self.playback_trace_id: str = playback_trace_id
        self.playback_state: str = playback_state

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

    @staticmethod
    def construct_from_use_case_execution(use_case_execution):
        return DummyUseCaseExecution(use_case=use_case_execution.use_case,
                                     computed=use_case_execution.computed,
                                     verified=use_case_execution.is_verified(),
                                     playback_trace_id=use_case_execution.playback_trace_id,
                                     playback_state=use_case_execution.playback_state)

    def is_computed(self) -> bool:
        return self.computed

    # def is_verified(self) -> bool:
    #     return len(self.get_playback_traces()) > 0
