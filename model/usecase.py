# -*- coding: utf-8 -*-
from typing import List

from model.atd import ATD


class UseCase:
    def __init__(self, name):
        self.name = UseCase.purge_name(name)
        # References to other use cases
        self.use_cases = []
        self.atds: List[ATD] = []
        # All the atds from all referenced use cases
        self.atds_flatted: List[ATD] = []

    def __str__(self):
        return f"UseCase(name={self.name} atds={[str(atd) for atd in self.atds]} atds_flatted={[str(atd) for atd in self.atds_flatted]})"

    def __eq__(self, o):
        return self.name == o.name

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def use_cases_to_names_set(use_cases):
        return {uc.name for uc in use_cases}

    @staticmethod
    def use_cases_to_str(use_cases):
        use_cases_name = [uc.name for uc in use_cases]
        return ', '.join(use_cases_name)

    @staticmethod
    def purge_name(name):
        return name.strip()

    def contains_feature_flatted(self, feature):
        return any(atd.target_descriptor == feature for atd in self.atds_flatted)

    def contains_features_flatted(self, features):
        features_in = []
        for f in features:
            if self.contains_feature_flatted(f):
                features_in.append(f)
        return features_in

    def get_target_descriptor_flatted(self):
        return [atd.target_descriptor for atd in self.atds]

    def to_string_short(self):
        return f"UseCase(name={self.name} " \
               f"atds={[atd.target_descriptor for atd in self.atds]} " \
               f"atds_flatted={[atd.target_descriptor for atd in self.atds_flatted]})"
