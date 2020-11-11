# -*- coding: utf-8 -*-
import collections
from functools import lru_cache
from typing import List

from model.usecase import UseCase
from model.atd import ATD
from usecasemapping import FILTERED_USE_CASES

PROCESS_SNIPPET_STARTING_TAG = "#"
PROCESS_SNIPPET_COMMENT_SYMBOL = "//"
PROCESS_SNIPPET_UNASSIGNED_TAG = "#unassigned"


class UseCaseReader(object):
    """
    For parsing details see: saarland.cispa.pst.utils.ProcessSnippetParser
    """

    @staticmethod
    @lru_cache(maxsize=8)
    def construct_use_case_definitions(atd_path):
        feature_use_cases_map = collections.defaultdict(set)
        use_cases: List[UseCase] = []
        name_use_case_map = {}
        use_case_curr = None
        unassigned_atds = []
        # When PROCESS_SNIPPET_UNASSIGNED_TAG reached then read till the end of the file and everything
        # in between are unassigned ATDs. Therefore, no use cases in between and afterwards are allowed.
        unassigned_reading_state = False

        with open(atd_path) as f:
            for line in f:
                assert not unassigned_reading_state
                if line and line not in ['\n', '\r\n'] and not line.startswith(
                        PROCESS_SNIPPET_COMMENT_SYMBOL):
                    line = line.replace('\n', '')
                    line = line.replace('\r\n', '')
                    if line.startswith(PROCESS_SNIPPET_UNASSIGNED_TAG):
                        unassigned_atds = UseCaseReader.construct_unassigned_atds(f)
                        unassigned_reading_state = True
                    elif line.startswith(PROCESS_SNIPPET_STARTING_TAG):
                        name = line.replace(PROCESS_SNIPPET_STARTING_TAG, "")
                        use_case_curr = UseCase(name)
                        use_cases.append(use_case_curr)
                        name_use_case_map[name] = use_case_curr
                    else:
                        entries = line.split('"')
                        if len(entries) == 1:
                            # At first add the raw name as string
                            use_case_curr.use_cases.append(entries[0])
                        elif len(entries) == 3:
                            target_descriptor = entries[1]
                            atd = ATD(entries[0], target_descriptor)
                            use_case_curr.atds.append(atd)
                            feature_use_cases_map[target_descriptor].add(use_case_curr)
                        elif len(entries) == 5:
                            target_descriptor = entries[1]
                            atd = ATD(entries[0], target_descriptor, entries[3])
                            use_case_curr.atds.append(atd)
                            feature_use_cases_map[target_descriptor].add(use_case_curr)
                        else:
                            raise ValueError(f"Not expected length: {line}")
        # Postprocess the use cases, because we have to resolve potential use case names to use case objects
        for uc in use_cases:
            uc.use_cases = [name_use_case_map[uc_name] for uc_name in uc.use_cases]

        for uc in use_cases:
            uc.atds_flatted = UseCaseReader.flatted_atds(uc)

        # UseCaseReader.pretty_print(name_use_case_map)

        assert len(use_cases) == len(set(use_cases)) and len(use_cases) == len(set([uc.name for uc in use_cases]))

        # Filter blackisted use cases like email, name, birthday
        use_cases = list(filter(lambda use_case: not any(black_listed_uc.lower() == use_case.name.lower() for black_listed_uc in FILTERED_USE_CASES), use_cases))

        return use_cases, unassigned_atds, feature_use_cases_map

    @staticmethod
    @lru_cache(maxsize=8)
    def construct_unassigned_atds(f):
        atds = []
        for line in f:
            if line and line not in ['\n', '\r\n'] and not line.startswith(PROCESS_SNIPPET_COMMENT_SYMBOL):
                line = line.replace('\n', '')
                line = line.replace('\r\n', '')
                entries = line.split('"')
                if len(entries) == 3:
                    atd = ATD(entries[0], entries[1])
                elif len(entries) == 5:
                    atd = ATD(entries[0], entries[1], entries[3])
                else:
                    raise ValueError(f"Not expected length: {line}")
                atds.append(atd)
        return atds

    @staticmethod
    @lru_cache(maxsize=256)
    def flatted_atds(use_case):
        top_level_atds = use_case.atds
        flatted_atds = []
        for uc in use_case.use_cases:
            flatted_atds += UseCaseReader.flatted_atds(uc)

        return top_level_atds + flatted_atds

    @staticmethod
    def pretty_print(name_use_case_map):
        """
        Helper function to add new use cases to the [appusecasemapping].
        """
        names = [f'"{name}",' for name in name_use_case_map.keys()]
        names.sort()

        for name in names:
            print(name)
