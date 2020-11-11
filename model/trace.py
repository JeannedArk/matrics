# -*- coding: utf-8 -*-
import os
import uuid

from model.transition import Transition
from model.usecase import UseCase
from usecaseclassification.processor.transitionselectionstrategy import TransitionSelectionBySequence
from usecaseclassification.tsequence import TSequence
from util.modelutil import get_csv_dict_reader, get_csv_writer
from util.typeutil import convert_bool_kotlin, convert_bool_python


FIELDNAME_SOURCE_STATE = 'Source State'
FIELDNAME_RESULTING_STATE = 'Resulting State'
FIELDNAME_INTERACTED_WIDGET = 'Interacted Widget'
FIELDNAME_ACTION_ID = 'Action-Id'
FIELDNAME_ACTION = 'Action'
FIELDNAME_START_TIME = 'StartTime'
FIELDNAME_END_TIME = 'EndTime'
FIELDNAME_SUCCESSFUL = 'SuccessFul'
FIELDNAME_EXCEPTION = 'Exception'
FIELDNAME_DATA = 'Data'
FIELDNAME_HAD_RESULT_SCREEN = 'HasResultScreen'
FIELDNAME_CUSTOM = 'Custom'

# In the order how it is dumped in trace.csv files
FIELDNAMES = [
    FIELDNAME_SOURCE_STATE,
    FIELDNAME_ACTION,
    FIELDNAME_INTERACTED_WIDGET,
    FIELDNAME_RESULTING_STATE,
    FIELDNAME_START_TIME,
    FIELDNAME_END_TIME,
    FIELDNAME_SUCCESSFUL,
    FIELDNAME_EXCEPTION,
    FIELDNAME_DATA,
    FIELDNAME_ACTION_ID,
    FIELDNAME_HAD_RESULT_SCREEN,
    FIELDNAME_CUSTOM,
]


class Trace(object):
    def __init__(self, transitions, unique_id=None, meta_data=None):
        self.transitions = transitions
        self.unique_id = unique_id
        self.meta_data = meta_data if meta_data is not None else [None for t in self.transitions]
        assert len(self.transitions) == len(self.meta_data),\
            f"Transitions len was {len(self.transitions)}, meta data len was {self.meta_data}"
        self.sequence = TSequence.construct_from_transitions(transitions)
        self.network_pages = set()
        self.idx: int = None
        self.app_home_state: str = None

    def __str__(self) -> str:
        transitions_str = '\n'.join([str(trans) for trans in self.transitions])
        return f"Trace({self.unique_id})\n{transitions_str}"

    @staticmethod
    def construct_from_trace_file(trace_file, uid_state_map, uid_widget_map, actionid_transition_map):
        with open(trace_file, newline='') as f:
            unique_id = os.path.basename(trace_file).replace("trace", "").replace(".csv", "")
            transitions = []
            csvreader = get_csv_dict_reader(f)
            for row in csvreader:
                src_state_uid = row[FIELDNAME_SOURCE_STATE]
                res_state_uid = row[FIELDNAME_RESULTING_STATE]
                w_uid = row[FIELDNAME_INTERACTED_WIDGET]
                iwidget = None if w_uid not in uid_widget_map else uid_widget_map[w_uid]
                custom = row[FIELDNAME_CUSTOM] if FIELDNAME_CUSTOM in row else ""
                actionId = row[FIELDNAME_ACTION_ID]
                try:
                    src_state = uid_state_map[src_state_uid]
                    res_state = uid_state_map[res_state_uid]
                    transition = Transition(src_state_uid,
                                            src_state,
                                            row[FIELDNAME_ACTION],
                                            w_uid,
                                            iwidget,
                                            res_state_uid,
                                            res_state,
                                            row[FIELDNAME_START_TIME],
                                            row[FIELDNAME_END_TIME],
                                            convert_bool_python(row[FIELDNAME_SUCCESSFUL]),
                                            row[FIELDNAME_EXCEPTION],
                                            row[FIELDNAME_DATA],
                                            actionId,
                                            convert_bool_python(row[FIELDNAME_HAD_RESULT_SCREEN]),
                                            custom)
                    transitions.append(transition)
                    actionid_transition_map[actionId] = transition
                    src_state.outgoing_transitions.add(transition)
                    res_state.action_ids.add(actionId)
                except KeyError as err:
                    raise KeyError(f"KeyError: trace_file: {trace_file} src_state_uid: {src_state_uid} orig err: {err}")

        return Trace(transitions=transitions, unique_id=unique_id)

    @staticmethod
    def construct_from_path(exploration_model, path):
        transition_selector = TransitionSelectionBySequence(exploration_model=exploration_model)
        transitions, transformed_meta_data = transition_selector.select(path=path)
        transitions = transition_selector.post_process(transitions)
        return Trace(transitions=transitions, meta_data=transformed_meta_data)

    def dump_to_file(self, target_dir):
        """
        Trace file header:
        Source State;Action;Interacted Widget;Resulting State;StartTime;EndTime;SuccessFul;Exception;Data;Action-Id;HasResultScreen;Custom
        """
        trace_file = os.path.join(target_dir, self.get_trace_file_name())
        with open(trace_file, mode='w') as f:
            csvwriter = get_csv_writer(f, FIELDNAMES)

            csvwriter.writeheader()
            for trans in self.transitions:
                csvwriter.writerow({
                    FIELDNAME_SOURCE_STATE: trans.source_state,
                    FIELDNAME_ACTION: trans.action,
                    FIELDNAME_INTERACTED_WIDGET: trans.interacted_widget,
                    FIELDNAME_RESULTING_STATE: trans.resulting_state,
                    FIELDNAME_START_TIME: trans.start_time,
                    FIELDNAME_END_TIME: trans.end_time,
                    FIELDNAME_SUCCESSFUL: convert_bool_kotlin(trans.successful),
                    FIELDNAME_EXCEPTION: trans.exception,
                    FIELDNAME_DATA: trans.data,
                    FIELDNAME_ACTION_ID: trans.action_id,
                    FIELDNAME_HAD_RESULT_SCREEN: trans.has_result_screen,
                    FIELDNAME_CUSTOM: trans.custom,
                })

    def generate_trace_id(self, use_case: UseCase):
        self.unique_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{use_case.name}_{self.idx}")

    def get_trace_file_name(self):
        assert self.unique_id is not None
        return f"{self.idx}_trace{self.unique_id}.csv"
