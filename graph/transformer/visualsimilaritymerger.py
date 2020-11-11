# -*- coding: utf-8 -*-
import collections
from functools import lru_cache

from model.state import State
from util.util import shorten_fl

import imagehash
from PIL import Image

from graph.transformer.basegraphtransformer import BaseGraphTransformer


ANDROID_BAR_HEIGHT = 80


class VisualSimilarityMerger(BaseGraphTransformer):
    """
    http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

    At first dhash, fast, pretty good accuracy
    then phash high accuracy, cropping the bar
    """

    PHASH_EPSILON = 3

    def __init__(self, graph):
        self.g = graph
        self.transition_source_map = collections.defaultdict(list)
        self.transition_resulting_map = collections.defaultdict(list)
        self.image_hash_state_map = collections.defaultdict(list)
        self.initial_states_size = -1
        self.init()

    def init(self):
        self.initial_states_size = len(self.g.states)
        for state in self.g.states:
            img_avg_h = self.has_equivalent_images(state)
            if img_avg_h is not None:
                self.image_hash_state_map[img_avg_h].append(state)

        for trans in self.g.transitions:
            if trans.source_state_o is not None:
                self.transition_source_map[trans.source_state].append(trans)
            if trans.resulting_state_o is not None:
                self.transition_resulting_map[trans.resulting_state].append(trans)

    def print_latex_table(self):
        init_size = self.initial_states_size
        post_processing_size = len(self.g.states)
        proportion = (1 - (float(post_processing_size) / init_size)) * 100.0
        print(f"{self.g.package_name} & {init_size} & {post_processing_size} & {shorten_fl(proportion)} \\\\")

    def has_equivalent_images(self, state):
        if not state.image_paths:
            return None
        avg_h = set(self.get_avg_hash(image_path) for image_path in state.image_paths)
        p_h = set(self.get_phash(image_path) for image_path in state.image_paths)
        if len(avg_h) == 1 and len(p_h) == 1:
            return avg_h.pop()
        else:
            return None

    @lru_cache(maxsize=512)
    def get_avg_hash(self, image_path):
        """
        Crops the Android bar and uses the first image path.
        """
        return imagehash.average_hash(self.image_crop(image_path))

    def get_phash_from_state(self, state):
        assert state.image_paths
        return self.get_phash(next(iter(state.image_paths)))

    @lru_cache(maxsize=512)
    def get_phash(self, image_path):
        """
        Crops the Android bar and uses the first image path.
        """
        return imagehash.phash(self.image_crop(image_path))

    def image_crop(self, image_path):
        """
        1440 × 2560
        """
        img = Image.open(image_path)
        width, height = img.size
        area = (0, ANDROID_BAR_HEIGHT, width, height)
        cropped_img = img.crop(area)
        return cropped_img

    def transform(self):
        for k, states in self.image_hash_state_map.items():
            if len(states) > 1:
                # Try to merge every state with every state
                idx_1 = 0
                while idx_1 < len(states) - 1:
                    base_state = states[idx_1]
                    idx_2 = idx_1 + 1
                    while idx_2 < len(states):
                        state = states[idx_2]
                        if self.should_merge(base_state, state):
                            self.merge(base_state, state)
                            states.remove(state)
                        else:
                            idx_2 += 1

                    idx_1 += 1

    def should_merge(self, state_1: State, state_2: State) -> bool:
        # import os
        # if state_1.get_state_id_config() == state_2.get_state_id_config():
        #     if self.get_phash_from_state(state_1) - self.get_phash_from_state(state_2) < VisualSimilarityMerger.PHASH_EPSILON:
        #         return True
        #     else:
        #         state_1_image_path = next(iter(state_1.image_paths))
        #         cmd = f"open {state_1_image_path}; open {next(iter(state_2.image_paths))}"
        #         print(cmd)
        #         os.system(cmd)
        #         return False
        # else:
        #     return False
        return self.get_phash_from_state(state_1) - self.get_phash_from_state(state_2) < VisualSimilarityMerger.PHASH_EPSILON \
               and state_1.get_state_id_config() == state_2.get_state_id_config()

    def merge(self, state_1, state_2):
        assert state_1.unique_id != state_2.unique_id
        # print(f"Merge size: {len(self.g.states)} {state_1.unique_id} {state_2.unique_id}")

        self.g.states.remove(state_2)
        state_1.merge_with_state(state_2)

        for trans in self.transition_source_map[state_2.unique_id]:
            assert trans.source_state == state_2.unique_id
            trans.source_state = state_1.unique_id
            trans.source_state_o = state_1
        for trans in self.transition_resulting_map[state_2.unique_id]:
            assert trans.resulting_state == state_2.unique_id
            trans.resulting_state = state_1.unique_id
            trans.resulting_state_o = state_1
