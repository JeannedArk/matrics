import json
import os
from collections import namedtuple

from model.usecase import UseCase

IMAGE_DIR = "img"
IMG_PATH_DEFAULT = "/img/Default.png"
# We need this prefix for image files to route and serve these files, see app.py.
IMG_PATH_PREFIX = "/imgdir"
ATD_IMG_SUBDIR = "ATD"
RESIZE_IMG_SUBDIR = "RESIZE"


APKTOOL_PATH = os.path.join("resources/apktool.jar")


# ToGAPE config constants
TOGAPE_CFG_FEATURE_DIR = "ModelProperties.path.FeatureDir"
TOGAPE_CFG_IMAGES_SUB_DIR = "ModelProperties.path.imagesSubDir"
TOGAPE_CFG_EVALUATION_DIR = "evaluationDir"
TOGAPE_CFG_OUTPUT_DIR = "Output.outputDir"
TOGAPE_CFG_EXPLORATION_APKS_DIR = "Exploration.apksDir"
TOGAPE_CFG_ATD_PATH = "atdPath"

TOGAPE_MODEL_DIR_NAME = "model"
TOGAPE_MODEL_STATES_DIR_NAME = "states"

# Old exploration
TOGAPE_CONFIG_FILE_SOCIAL = "./togapeconfigs/ase-configSocialBase.properties"
TOGAPE_CONFIG_FILE_RECIPE = "./togapeconfigs/ase-configRecipeBase.properties"
TOGAPE_CONFIG_FILE_DATING = "./togapeconfigs/ase-configDatingBase.properties"
TOGAPE_CONFIG_FILE_TRAVEL = "./togapeconfigs/ase-configTravelBase.properties"
# Better exploration with keyword map
TOGAPE_CONFIG_FILE_SOCIAL_2 = "./togapeconfigs/ase-configSocialBase2.properties"
TOGAPE_CONFIG_FILE_RECIPE_2 = "./togapeconfigs/ase-configRecipeBase2.properties"
TOGAPE_CONFIG_FILE_DATING_2 = "./togapeconfigs/ase-configDatingBase2.properties"
TOGAPE_CONFIG_FILE_TRAVEL_2 = "./togapeconfigs/ase-configTravelBase2.properties"

TOGAPE_CONFIG_FILE_ALL = "./togapeconfigs/ase-configAllBase2.properties"


# Matrics config constants
MATRICS_CFG_APP_FILTER_LIST = "app.filter"
MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS = "usecase.compute_executions"
MATRICS_CFG_COMPUTE_USE_CASE_EXECUTIONS_DEFAULT = True
MATRICS_CFG_MODEL_ACCESSOR_SELECTION = "model_accessor.execution_selection"

MATRICS_PLAYBACK_MODEL_DIR_NAME = "matricsplayback"
TOGAPE_FEATURE_DIR_NAME = "feature-logs"
MATRICS_PLAYBACK_ITERATION_NUMBER = 5
PLAYBACK_RESULTS_CSV_PREFIX = "playbackresults-"
MATRICS_NUMBER_OF_PATH_SELECTION = 10
MATRICS_UCE_DISPLAY_DATAPOINT_THRESHOLD = 10

# Matrics plots
MATRICS_FIGURE_IMAGE_DIR_NAME = "matricsplots"
MATRICS_FIGURE_FILE_EXTENSION = ".pdf"
MATRICS_FIGURE_DUMP_PLOTS = False
MATRICS_FIGURE_FONT_SIZE = 12
MATRICS_FIGURE_FONT_FAMILY = "Times New Roman"
MATRICS_FIGURE_DASH_STYLE = "dash"
MATRICS_FIGURE_LINE_WIDTH = 2
MATRICS_FIGURE_DEFAULT_HEIGHT = 450
MATRICS_FIGURE_DEFAULT_PADDING = 200
MATRICS_FIGURE_VERTICAL_HEIGHT_PER_ENTRY = 70

# MATRICS_VISUALIZATION_WIDTH = "2000px"
MATRICS_VISUALIZATION_WIDTH = "100%"
MATRICS_TAG_APP_HOME_STATE = False

# Matrics cache
MATRICS_CACHE_DIR_NAME = "matricscacheNew"
MATRICS_CACHE_READ = False
MATRICS_CACHE_DUMP = False

# Matrics value dump
MATRICS_DUMP_VALUE_DIR_NAME = "matricsvalues"
MATRICS_DUMP_VALUE = False


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())


def get_json_config(config_file):
    with open(config_file) as json_file:
        return json.load(json_file, object_hook=_json_object_hook)


def get_properties_config(config_file, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(config_file, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props


def validate_togape_config(config_togape):
    entries = [
        TOGAPE_CFG_FEATURE_DIR,
        TOGAPE_CFG_IMAGES_SUB_DIR,
        TOGAPE_CFG_EVALUATION_DIR,
        TOGAPE_CFG_OUTPUT_DIR,
        TOGAPE_CFG_EXPLORATION_APKS_DIR,
        TOGAPE_CFG_ATD_PATH
    ]

    for e in entries:
        try:
            config_togape[e]
        except KeyError:
            raise KeyError(f"The entry {e} needs to be present in the ToGAPE properties file.")


NULL_OUT_CHAR = "0"
NULL_OUT_CNT_LAST_ELEMENTS = 6


def get_unique_trace_id(base_id: str, idx: int):
    """
    NOT USED ANYMORE


    This is not elegant.
    Index is encoded in the end of unique_id string.
    """
    l = len(base_id)
    idx_str = str(idx)
    unique_id = base_id[:l - NULL_OUT_CNT_LAST_ELEMENTS]
    unique_id += ''.join([NULL_OUT_CHAR for i in range(NULL_OUT_CNT_LAST_ELEMENTS - len(idx_str))])
    unique_id += idx_str
    return unique_id


PADDED_MAX_LENGTH = 8 + 4 + 4 + 4
LEN_ORIG_TRACE = len("fe510feb-1e85-4051-b489-4eff72703499")

def get_unique_trace_id_from_use_case(use_case: UseCase, idx: int):
    """
    NOT USED ANYMORE


    Index is encoded in the end of unique_id string.

    Example original trace name:
    tracefe510feb-1e85-4051-b489-4eff72703499
    fe510feb-1e85-4051-b489-4eff72703499
    8 - 4 - 4 - 4 - 12

    returns example: Search_f-or_p-osts-0000-000000000003
    """
    name = use_case.name
    idx_str = str(idx)

    name_shortened = name[:PADDED_MAX_LENGTH]
    name_padded = name_shortened + ''.join([NULL_OUT_CHAR for i in range(PADDED_MAX_LENGTH - len(name_shortened))])
    s = f"{name_padded[:8]}-{name_padded[8:12]}-{name_padded[12:16]}-{name_padded[16:20]}-"
    s += ''.join([NULL_OUT_CHAR for i in range(12 - len(idx_str))]) + idx_str

    assert len(s) == LEN_ORIG_TRACE

    return s
