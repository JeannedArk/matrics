# -*- coding: utf-8 -*-
from typing import List

from model.androidapp import App
from model.usecase import UseCase
from usecaseclassification.usecaseexecution import UseCaseExecution


class AggregatedUseCaseExecution(object):
    # def __init__(self, app, use_case: UseCase, use_case_executions):
    def __init__(self, use_case: UseCase, apps: List[App], use_case_executions: List[UseCaseExecution]):
        # self.app = app
        self.use_case_executions = use_case_executions
        self.use_case = use_case
        # self.use_case_executions = use_case_executions
        self.apps = apps

    # Rethink this
    # def get_representative_use_case_execution(self):
    #     # The first execution
    #     return self.use_case_executions[0]
