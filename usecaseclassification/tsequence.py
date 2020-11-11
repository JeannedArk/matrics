# -*- coding: utf-8 -*-
from functools import lru_cache

from metadata import MetaData
from model.transition import Transition
from util import droidmateutil


class SequenceElement(object):
    def __init__(self, first_transition):
        self.transitions = [first_transition]
        self.source_state_o = first_transition.source_state_o
        self.resulting_state_o = None

    def add_transition(self, trans):
        self.transitions.append(trans)

    def finalize(self):
        self.resulting_state_o = self.transitions[-1].resulting_state_o

    def get_first_non_queue_transition(self):
        return next(trans
                    for trans in self.transitions
                    if not droidmateutil.is_queue_start_or_end(trans))

    @lru_cache(maxsize=1)
    def get_flatted_representation(self, meta_data=MetaData()):
        """
        Trans 1: A -> B
        Trans 2: B -> C
        Trans 3 Q-Start: C -> D
        Trans 4: C -> D
        Trans 5: C -> D
        Trans 6 Q-End: C -> D
        Trans 7: D -> E

        :returns:
        states = [A, B, C, D, D, D, D, E]
        transitions = [A -> B, B -> C, C -> D, D -> D, D -> D, D -> D, D -> E]
        """
        transitions = []
        states = []
        flatted_meta_data = MetaData()
        last_res_s = None
        processing_queue = False
        for trans in self.transitions:
            src_s = trans.source_state_o
            res_s = trans.resulting_state_o
            if processing_queue:
                states.append(res_s)
                new_trans = Transition(trans.resulting_state,
                                       trans.resulting_state_o,
                                       trans.action,
                                       trans.interacted_widget,
                                       trans.interacted_widget_o,
                                       trans.resulting_state,
                                       trans.resulting_state_o,
                                       trans.start_time,
                                       trans.end_time,
                                       trans.successful,
                                       trans.exception,
                                       trans.data,
                                       trans.action_id,
                                       trans.has_result_screen,
                                       trans.custom)
                transitions.append(new_trans)
                # We copy the data of the sequence element within the original meta data and apply to the
                # flatted states and transition representation
                if self in meta_data.data:
                    flatted_meta_data.put(res_s, meta_data.get(self))
                    flatted_meta_data.put(new_trans, meta_data.get(self))
            else:
                if last_res_s != src_s:
                    states.append(src_s)
                    if self in meta_data.data:
                        flatted_meta_data.put(src_s, meta_data.get(self))
                states.append(res_s)
                transitions.append(trans)
                # We copy the data of the sequence element within the origin meta data and apply to the
                # flatted states and transition representation
                if self in meta_data.data:
                    flatted_meta_data.put(res_s, meta_data.get(self))
                    flatted_meta_data.put(trans, meta_data.get(self))
                last_res_s = res_s

            if droidmateutil.is_queue_start(trans):
                processing_queue = True
            if droidmateutil.is_queue_end(trans):
                processing_queue = False
        return states, transitions, flatted_meta_data

    def pruned_length(self):
        """
        Return the actual length. We don't want queue head or tails to be accounted.
        """
        if len(self.transitions) == 1:
            return 1
        else:
            return sum(0 if droidmateutil.is_queue_start_or_end(trans) else 1
                       for trans in self.transitions)

    def graph_info(self):
        def trans_info(transitions):
            return "\n".join(trans.graph_info() for trans in transitions)
            # return "\n".join(f"T: {trans.source_state} -> {trans.resulting_state}" for trans in transitions)
        return f"Source state: {self.source_state_o.unique_id}\n" \
               f"Resulting state: {self.resulting_state_o.unique_id}\n" \
               f"Transitions:\n" \
               f"{trans_info(self.transitions)}"


class TSequence(object):
    """
    Sequence encapsulating transitions.
    """

    def __init__(self, transitions, seq_elements):
        self.transitions = transitions
        self.seq_elements = seq_elements

    def __hash__(self) -> int:
        return hash(tuple(self.transitions))

    @staticmethod
    def construct_from_transitions(transitions):
        seq_elements = []
        processing_queue = False
        current_seq_elem: SequenceElement = None
        for trans in transitions:
            if droidmateutil.is_queue_end(trans):
                assert processing_queue
                current_seq_elem.add_transition(trans)
                current_seq_elem.finalize()
                seq_elements.append(current_seq_elem)
                current_seq_elem = None
                processing_queue = False
            elif droidmateutil.is_queue_start(trans):
                assert not processing_queue
                assert current_seq_elem is None
                processing_queue = True
                current_seq_elem = SequenceElement(trans)
            else:
                if processing_queue:
                    current_seq_elem.add_transition(trans)
                else:
                    assert current_seq_elem is None
                    seq_elem = SequenceElement(trans)
                    seq_elem.finalize()
                    seq_elements.append(seq_elem)

        assert not processing_queue

        return TSequence(transitions=transitions, seq_elements=seq_elements)

    @staticmethod
    def construct_from_sequence_elements(seq_elements):
        transitions = [trans
                       for seq_elem in seq_elements
                       for trans in seq_elem.transitions]
        return TSequence(transitions=transitions, seq_elements=seq_elements)

    @lru_cache(maxsize=1)
    def get_flatted_representation(self, meta_data=MetaData()):
        """
        Trans 1: A -> B
        Trans 2: B -> C
        Trans 3 Q-Start: C -> D
        Trans 4: C -> D
        Trans 5: C -> D
        Trans 6 Q-End: C -> D
        Trans 7: D -> E

        :returns:
        states = [A, B, C, D, D, D, D, E]
        transitions = [A -> B, B -> C, C -> D, D -> D, D -> D, D -> D, D -> E]
        """
        transitions = []
        states = []
        flatted_meta_data = MetaData()
        for seq_elem in self.seq_elements:
            tmp_states, tmp_transitions, tmp_meta_data = seq_elem.get_flatted_representation(meta_data=meta_data)
            states.extend(tmp_states)
            transitions.extend(tmp_transitions)
            flatted_meta_data.merge(tmp_meta_data)
        return states, transitions, flatted_meta_data

    def pruned_length(self):
        return sum(seq_elem.pruned_length() for seq_elem in self.seq_elements)
