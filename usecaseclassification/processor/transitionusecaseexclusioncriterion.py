# -*- coding: utf-8 -*-
from model.transition import Transition
from criterion.basecriterion import BaseCriterion
from usecaseclassification.processor.transitionadvertisementcriterion import TransitionAdvertisementCriterion
from usecaseclassification.tsequence import SequenceElement
from util import droidmateutil


class TransitionUseCaseExclusionCriterion(BaseCriterion):
    def __init__(self, exploration_model):
        self.exploration_model = exploration_model
        self.home_state = self.exploration_model.home_state
        self.ad_exclusion_criterion = TransitionAdvertisementCriterion()

    def decide(self, elem):
        if isinstance(elem, Transition):
            return self.decide_transition(elem)
        elif isinstance(elem, SequenceElement):
            return self.decide_sequence_element(elem)
        else:
            raise ValueError(f"Unknown type was passed: {elem}")

    def decide_sequence_element(self, seq_elem: SequenceElement):
        """
        Returns True, if the transition should be excluded.
        Returns False, if the transition should be not excluded.
        """
        # The criterion must apply for transitions in the sequence element
        return any(self.decide_transition_pure(trans) for trans in seq_elem.transitions)

    def decide_transition_pure(self, trans: Transition):
        """
        Returns True, if the transition should be excluded.
        Returns False, if the transition should be not excluded.
        """
        # Do not add transitions that include a terminate, because we don't need these transitions.
        # We can terminate from every transition.
        # TODO Really do not allow back transitions?
        # Do not add transitions that are not successful, these are not desired.
        # Only allow LaunchApp transitions which source state is a homescreen. Otherwise the shortest path
        # algorithm can chose paths that include LaunchApp transitions inbetween to chose a shorter invalid
        # path.
        # Do not add transitions that go back to a homestate, we want stay within the app.
        # Do not allow transitions that interact with advertisement.

        return droidmateutil.is_terminate(trans)\
               or not trans.successful\
               or droidmateutil.is_press_back(trans)\
               or (droidmateutil.is_launch_app(trans) and not self.home_state.unique_id == trans.source_state_o.unique_id) \
               or trans.resulting_state_o.unique_id == self.home_state.unique_id \
               or self.ad_exclusion_criterion.decide(trans)

    def decide_transition(self, trans: Transition):
        """
        Returns True, if the transition should be excluded.
        Returns False, if the transition should be not excluded.
        """
        # TODO comment: Additionally do not allow queue start and end and close keyboard

        return self.decide_transition_pure(trans)\
            or droidmateutil.is_queue_start(trans)\
            or droidmateutil.is_queue_end(trans) \
            or droidmateutil.is_close_keyboard(trans)
