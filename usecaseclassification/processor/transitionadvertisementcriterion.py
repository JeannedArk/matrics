# -*- coding: utf-8 -*-
from model.transition import Transition
from criterion.basecriterion import BaseCriterion


class TransitionAdvertisementCriterion(BaseCriterion):
    def decide(self, trans: Transition):
        i_widget = trans.interacted_widget_o
        if i_widget is None:
            return False
        return i_widget.hint_text == "earnamoney.com" or i_widget.displayed_text == "Test Ad"
