# -*- coding: utf-8 -*-
from enum import Enum
from abc import ABCMeta, abstractmethod
from typing import List

from usecaseclassification.aggregatedsecaseexecution import AggregatedUseCaseExecution


class AggregationLevel(Enum):
    """
    TODO think about USE_CASE_STATE and APP_STATE etc.
    because right now STATE means APP_STATE
    """
    APP = "app"
    STATE = "state"
    FEATURE = "feature"
    USE_CASE = "use_case"

    def iter_instance(self, model):
        if self.name == AggregationLevel.APP.name:
            return AppAggregationLevelIterator(iterator=model.apps, use_all_indices=True)
        elif self.name == AggregationLevel.STATE.name:
            return StateAggregationLevelIterator(iterator=model.apps, use_all_indices=True)
        else:
            raise NotImplementedError(f"Not implemented yet for {self.name}")

    def iter_metric(self, model):
        if self.name == AggregationLevel.APP.name:
            return [AppAggregationLevelIterator(model.apps)]
        elif self.name == AggregationLevel.STATE.name:
            return [StateAggregationLevelIterator(model.apps)]
        elif self.name == AggregationLevel.USE_CASE.name:
            # For every use case construct an AggregatedUseCaseExecution containing all apps that have this kind of
            # use case execution and the corresponding use case execution
            use_cases = model.use_case_manager.get_use_cases()
            iterator_ls = []
            for use_case in use_cases:
                use_case_executions = []
                apps = []
                for app in model.apps:
                    if app.exploration_model.use_case_execution_manager.has_use_case(use_case):
                        use_case_executions.append(app.exploration_model.use_case_execution_manager.get_use_case_execution(use_case))
                        apps.append(app)
                if use_case_executions:
                    aggregated_use_case = AggregatedUseCaseExecution(use_case=use_case, apps=apps, use_case_executions=use_case_executions)
                    iterator_ls.append(UseCaseAggregationLevelIterator(aggregated_use_case))
            return iterator_ls
        else:
            raise NotImplementedError(f"Not implemented yet for {self.name}")

    def str_short(self) -> str:
        if self.name == AggregationLevel.APP.name:
            return f"AL.App"
        elif self.name == AggregationLevel.STATE.name:
            return f"AL.State"
        elif self.name == AggregationLevel.USE_CASE.name:
            return f"AL.Use case"
        else:
            raise NotImplementedError(f"Not implemented yet for {self.name}")

    def texify(self) -> str:
        if self.name == AggregationLevel.APP.name:
            return f"App"
        elif self.name == AggregationLevel.STATE.name:
            return f"State"
        elif self.name == AggregationLevel.USE_CASE.name:
            return f"UCE"
        else:
            raise NotImplementedError(f"Not implemented yet for {self.name}")


class BaseAggregationLevelIterator(metaclass=ABCMeta):
    def __init__(self, aggregation_level, iterator, all_indices, use_all_indices):
        """
        :param use_all_indices: Determines whether all_indices or only indices should be used, i.e. returned when
        calling get_indices().  Some metrics of apps might contain not valid data (not a number because there were none
        of the desired elements) and therefore this app/index should be discarded.
        """
        self.aggregation_level = aggregation_level
        self.iterator = iterator
        self.all_indices = all_indices
        self.indices = []
        self.use_all_indices = use_all_indices

    def add_index(self, idx: int):
        self.indices.append(self.all_indices[idx])

    def get_index(self, idx: int) -> str:
        return self.all_indices[idx]

    def get_indices(self) -> List[str]:
        return self.all_indices if self.use_all_indices else self.indices

    def set_indices(self, indices: List[str]):
        if self.use_all_indices:
            self.all_indices = indices
        else:
            self.indices = indices

    @abstractmethod
    def title(self):
        pass

    def iter(self):
        return self.iterator


class AppAggregationLevelIterator(BaseAggregationLevelIterator):
    def __init__(self, iterator, use_all_indices=False):
        super().__init__(aggregation_level=AggregationLevel.APP,
                         iterator=iterator,
                         all_indices=[app.short_name for app in iterator],
                         use_all_indices=use_all_indices)

    def title(self):
        return f"{self.aggregation_level.value}"


class StateAggregationLevelIterator(BaseAggregationLevelIterator):
    def __init__(self, iterator, use_all_indices=False):
        super().__init__(aggregation_level=AggregationLevel.STATE,
                         iterator=iterator,
                         all_indices=[app.short_name for app in iterator],
                         use_all_indices=use_all_indices)

    def title(self):
        return f"{self.aggregation_level.value}"


class UseCaseAggregationLevelIterator(BaseAggregationLevelIterator):
    def __init__(self, aggregated_use_case_execution: AggregatedUseCaseExecution, use_all_indices=False):
        super().__init__(aggregation_level=AggregationLevel.USE_CASE,
                         iterator=aggregated_use_case_execution.use_case_executions,
                         all_indices=[app.short_name for app in aggregated_use_case_execution.apps],
                         use_all_indices=use_all_indices)
        self.use_case = aggregated_use_case_execution.use_case
        assert aggregated_use_case_execution.apps
        assert aggregated_use_case_execution.use_case_executions
        assert len(aggregated_use_case_execution.apps) == len(aggregated_use_case_execution.use_case_executions)

    def title(self):
        return f"{self.aggregation_level.texify()} ({self.use_case.name})"
