# -*- coding: utf-8 -*-
from typing import List

import appdomainmapping
import usecasemapping
from model.usecase import UseCase
from usecaseclassification.usecasereader import UseCaseReader


class UseCaseManager(object):
    def __init__(self, atd_path):
        self.atd_path = atd_path
        self.use_cases, self.unassigned_atds, self.feature_use_cases_map = UseCaseReader.construct_use_case_definitions(atd_path)

    def get_use_case_data(self):
        return self.use_cases, self.unassigned_atds, self.feature_use_cases_map

    def get_use_cases(self) -> List[UseCase]:
        return self.use_cases

    def get_use_cases_for_domain(self, domain: appdomainmapping.Domain):
        return [use_case
                for use_case in self.use_cases
                if use_case.name in usecasemapping.USE_CASE_DOMAIN_MAP[domain]]
