import logging
import os
from functools import total_ordering
from typing import Optional

import appdomainmapping
from libraryextractor import LibraryExtractor
from model.dummyexplorationmodel import DummyExplorationModel
from model.explorationmodel import ExplorationModel
from shortnamemapping import APP_SHORT_NAME_MAP
from usecaseclassification.usecasemanager import UseCaseManager
from util import configutil


# Unfortunately pickle cannot handle the cyclic data structures and fixing this would be really complex.
# Therefore, we don't load the exploration model from a dump.
LOAD_EXPLORATION_MODEL_FROM_FILE_DUMP = False


@total_ordering
class App(object):
    def __init__(self, app_path, output_dir=None):
        from androguard.core.bytecodes.apk import APK
        from androguard.core.androconf import show_logging
        show_logging(level=logging.CRITICAL)

        self.app_path = app_path
        self.apk = APK(app_path)
        self.package_name = self.apk.get_package()
        self.domain = appdomainmapping.get_domain(self.package_name)
        self.permissions = self.apk.get_permissions()
        self.version_name = self.apk.get_androidversion_name()
        self.receivers = self.apk.get_receivers()
        self.activities = self.apk.get_activities()
        self.app_size = self.compute_app_size()
        # self.possible_broadcasts = self.get_possible_broadcasts()
        self.exploration_model: Optional[ExplorationModel] = None
        self.ad_tracking_libraries = set()
        self.short_name: str = self.get_short_name()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, App):
            return self.package_name == o.package_name
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.package_name)

    def __lt__(self, other):
        if self.domain == other.domain:
            return self.package_name < other.package_name
        else:
            return self.domain < other.domain

    def get_short_name(self) -> str:
        assert self.package_name in APP_SHORT_NAME_MAP, f"{self.package_name} is not present in APP_SHORT_NAME_MAP"
        return APP_SHORT_NAME_MAP[self.package_name]

    def compute_app_size(self):
        """
        :return: The app file size in MB.
        """
        return os.path.getsize(self.app_path) / (1024 * 1024.0)

    def construct_data(self, config_togape, compute_use_case_executions, load_from_cache):
        togape_output_dir = config_togape[configutil.TOGAPE_CFG_OUTPUT_DIR]
        model_dir = os.path.join(togape_output_dir, configutil.TOGAPE_MODEL_DIR_NAME, self.package_name)
        feature_dir = config_togape[configutil.TOGAPE_CFG_FEATURE_DIR]
        # Actually only the file is needed oracle-PCK_NAME.json
        evaluation_dir = config_togape[configutil.TOGAPE_CFG_EVALUATION_DIR]
        matrics_playback_dir = os.path.join(togape_output_dir, configutil.MATRICS_PLAYBACK_MODEL_DIR_NAME)
        use_case_manager = UseCaseManager(config_togape[configutil.TOGAPE_CFG_ATD_PATH])
        if load_from_cache:
            self.exploration_model = DummyExplorationModel.create(app=self,
                                                                  package_name=self.package_name,
                                                                  exploration_model_dir=model_dir,
                                                                  use_case_manager=use_case_manager,
                                                                  matrics_playback_dir=matrics_playback_dir,
                                                                  compute_use_case_executions_b=LOAD_EXPLORATION_MODEL_FROM_FILE_DUMP)

        else:
            self.exploration_model = ExplorationModel.load_exploration_model(self,
                                                                             self.package_name,
                                                                             model_dir,
                                                                             feature_dir,
                                                                             evaluation_dir,
                                                                             use_case_manager,
                                                                             matrics_playback_dir,
                                                                             compute_use_case_executions,
                                                                             LOAD_EXPLORATION_MODEL_FROM_FILE_DUMP)
            self.ad_tracking_libraries = LibraryExtractor.get_ad_tracking_libraries(self.app_path, model_dir)
