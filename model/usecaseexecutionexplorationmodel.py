# -*- coding: utf-8 -*-
from graph import graph
from model.baseexplorationmodel import BaseExplorationModel


class UseCaseExecutionExplorationModel(BaseExplorationModel):
    def __init__(self, app, package_name, exploration_model_dir, feature_dir, evaluation_dir):
        super().__init__(app, package_name, exploration_model_dir, feature_dir, evaluation_dir)
        self.overall_graph: graph.Graph = self.create_graph()

        self.check_post_conditions()
