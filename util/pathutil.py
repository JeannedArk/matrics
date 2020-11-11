# -*- coding: utf-8 -*-
import os
import shutil

from util import configutil
from util.configutil import IMG_PATH_PREFIX, IMG_PATH_DEFAULT


def get_state_img(state_img):
    path = IMG_PATH_DEFAULT if state_img is None else state_img
    return os.path.join(IMG_PATH_PREFIX + path)


def filename_without_extension(path):
    return os.path.basename(path)


def append_subdir(path, dir_name):
    if os.path.isdir(path):
        return os.path.join(path, dir_name)
    else:
        assert os.path.isfile(path)
        filename = os.path.basename(path)
        dir_path = os.path.dirname(path)
        return os.path.join(dir_path, dir_name, filename)


def create_dir_if_non_existing(path):
    if not os.path.exists(path):
        os.makedirs(path)


def recreate_dir_safely(path):
    remove_dir_safely(path)
    os.makedirs(path)


def remove_dir_safely(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def get_figure_image_path(file_name) -> str:
    return os.path.abspath(os.path.join(configutil.MATRICS_FIGURE_IMAGE_DIR_NAME, f"{file_name}{configutil.MATRICS_FIGURE_FILE_EXTENSION}"))

# def append_to_filename(path, appendix):
#     """
#     Example:
#         path: a/b/c/bla.txt
#         new_filename: foo
#         returns a/b/c/foo.txt
#     """
#     return os.path.dirname(path)
