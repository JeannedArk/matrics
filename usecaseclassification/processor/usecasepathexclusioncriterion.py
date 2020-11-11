# -*- coding: utf-8 -*-
from criterion.basecriterion import BaseCriterion


class UseCasePathExclusionCriterion(BaseCriterion):
    """
    Exclusion criterion used for excluding paths connecting two states, NOT an overall path.
    """

    LENGTH_THRESHOLD = 7
    LENGTH_THRESHOLD_FROM_HOME_STATE = 10

    def decide(self, path: list, from_home_state = False):
        """
        :param path: list of nodes
        """
        if from_home_state:
            return len(path) > UseCasePathExclusionCriterion.LENGTH_THRESHOLD_FROM_HOME_STATE
        else:
            return len(path) > UseCasePathExclusionCriterion.LENGTH_THRESHOLD
