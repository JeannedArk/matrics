# -*- coding: utf-8 -*-
import logging
import os
import time
from typing import List

import plotly
from simpleaudio import _simpleaudio
from tqdm import tqdm
import multiprocessing as mp
import simpleaudio as sa

from model.androidapp import App
from model.model import Model
from outlierdetection.univariateoutlierdetection import ZScore1StdDevOutlierDetector
from util import configutil
from util.configutil import get_properties_config, MATRICS_CFG_APP_FILTER_LIST, MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS, \
    MATRICS_CFG_MODEL_ACCESSOR_SELECTION, MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS_DEFAULT
from util.util import shorten_fl


APK_SUFFIX = ".apk"
# This is just for me to quickly preventing ToGAPE to pick that app
APK_SUFFIX_CUSTOM = ".apk.B"

# Parallelization doesn't work because threading in python sucks
PARALLELIZE = False


class Matrics(object):
    """
    The main class of Matrics.
    """
    def __init__(self,
                 togape_config_file,
                 matrics_config=None,
                 debug_mode=True,
                 univariate_outlier_method=ZScore1StdDevOutlierDetector):
        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger('Matrics')

        self.togape_config_file = togape_config_file
        self.config_togape = get_properties_config(togape_config_file)
        configutil.validate_togape_config(self.config_togape)
        self.matrics_config = {} if matrics_config is None else matrics_config
        self.apk_dir = self.config_togape[configutil.TOGAPE_CFG_EXPLORATION_APKS_DIR]
        self.atd_path = self.config_togape[configutil.TOGAPE_CFG_ATD_PATH]
        self.logger.info(f'Using: {self.atd_path}')
        self.apps: List[App] = []
        self.pck_app_map = {}
        # self.univariate_outlier_method = univariate_outlier_method
        self.compute_use_case_executions = MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS_DEFAULT if MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS not in self.matrics_config else self.matrics_config[MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS]
        self.model = Model(self.apps, self.config_togape, self.matrics_config, univariate_outlier_method)

    def start(self):
        self.logger.info("Starting Matrics")
        self.logger.info(f"Using Plotly version: {plotly.__version__}")
        self.logger.info(f"Number of processors: {mp.cpu_count()}")
        start_time = time.time()

        self.setup()

        apps = []
        if PARALLELIZE:
            pool = mp.Pool(mp.cpu_count())
            try:
                apps = pool.map(self.analyze_app, [f_name for f_name in os.listdir(self.apk_dir)])
            finally:
                pool.close()
                pool.join()
        else:
            for f_name in tqdm(os.listdir(self.apk_dir), desc="Analyze app"):
                app = self.analyze_app(f_name)
                apps.append(app)

        for app in apps:
            if app is not None:
                self.apps.append(app)
                self.pck_app_map[app.package_name] = app

        assert len(self.apps) > 1, f"There must be at least two apks provided. Apk dir: {self.apk_dir}"
        assert (not MATRICS_CFG_APP_FILTER_LIST in self.matrics_config) or \
               all(any(cfg_package_name == app.package_name for app in self.apps) for cfg_package_name in self.matrics_config[MATRICS_CFG_APP_FILTER_LIST]),\
            f"Could not find a configured app: {self.matrics_config[MATRICS_CFG_APP_FILTER_LIST]}"
        print(f"Took: {shorten_fl(time.time() - start_time)}sec to construct app data")

        self.model.construct_metrics()
        print(f"Took: {shorten_fl(time.time() - start_time)}sec to construct metrics")
        self.play_sound(successful=True)

    def setup(self):
        if not os.path.exists(configutil.MATRICS_FIGURE_IMAGE_DIR_NAME):
            os.mkdir(configutil.MATRICS_FIGURE_IMAGE_DIR_NAME)
        if not os.path.exists(configutil.MATRICS_CACHE_DIR_NAME):
            os.mkdir(configutil.MATRICS_CACHE_DIR_NAME)
        if not os.path.exists(configutil.MATRICS_DUMP_VALUE_DIR_NAME):
            os.mkdir(configutil.MATRICS_DUMP_VALUE_DIR_NAME)

    def use_app_for_analysis(self, app: App):
        if MATRICS_CFG_APP_FILTER_LIST in self.matrics_config:
            return app.package_name in self.matrics_config[MATRICS_CFG_APP_FILTER_LIST]
        else:
            return True

    def analyze_app(self, f_name) -> App:
        """
        This logic was extracted into this function, because it can be also called asynchronously.
        Do not try to persist any data (by saving it to self. fields), because it gets called by
        process (not threads) and has no shared memory!
        """
        apk_file = os.path.join(self.apk_dir, f_name)
        if os.path.isfile(apk_file) and (f_name.endswith(APK_SUFFIX) or f_name.endswith(APK_SUFFIX_CUSTOM)):
            app = App(apk_file)
            if not self.use_app_for_analysis(app):
                return None
            self.logger.info(f"Analyze app: {f_name}")
            app.construct_data(self.config_togape, self.compute_use_case_executions, configutil.MATRICS_CACHE_READ)
            return app
        return None

    def get_app_from_pckg_name(self, pckg_name):
        for app in self.apps:
            if app.package_name == pckg_name:
                return app
        raise ValueError(f"Could not find an app for {pckg_name}")

    def play_sound(self, successful):
        try:
            if successful:
                sound_file = "resources/reeves_mxphone.wav"
            else:
                sound_file = "resources/explosion.wav"
            wave_obj = sa.WaveObject.from_wave_file(sound_file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except _simpleaudio.SimpleaudioError as e:
            print(e)
