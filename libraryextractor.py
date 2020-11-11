# -*- coding: utf-8 -*-
import os
import pickle

from util.configutil import APKTOOL_PATH


APKTOOL_OUTPUT_DIR = "apktool_output"
SMALI_FILE_SUFFIX = ".smali"
SMALI_RES_DIR_PREFIX = "smali"


def execute_cmd(cmd):
    # print(f"Execute cmd: {cmd}")
    ret = os.system(cmd)
    if ret != 0:
        raise ValueError(f"Command was not executed successfully\nReturn value: {ret}\nCommand: {cmd}")


def dot_to_slash(s: str):
    return s.replace(".", "/")


class LibraryExtractor(object):

    RESULTS_FILE_NAME = "library_result.matrics"
    PREFIX = "L"
    BLACKLIST_SMALI_DIRS = ["android", "androidx", "kotlin"]

    # Sources:
    # Manually checking apks
    # https://github.com/googleads/googleads-mobile-android-mediation/tree/master/ThirdPartyAdapters
    # https://admost.github.io/amrandroid/
    # https://arxiv.org/pdf/1303.0857.pdf from 2013
    AD_TRACKING_LIBRARIES = set([
        "cm.aptoide.pt.ads",
        "com.adcolony.sdk",
        "com.ad4screen.sdk",
        "com.adjust.sdk",
        "com.admob",
        "com.adwhirl",
        "com.appbrain",
        "com.applovin",
        "com.appboy",
        "com.appsflyer",
        "com.burstly",
        "com.cauly",
        "com.chartboost",
        "com.comscore",
        "com.duapps.ad",
        "com.facebook.ads",
        "com.flurry",
        "com.google.ads",
        "com.google.android.gms.ads",
        "com.google.analytics",
        "com.greystripe",
        "com.inmobi.ads",
        "com.integralads",
        "com.ironsource.mediationsdk",
        "com.jumptap",
        "com.moat.analytics",
        "com.mobclix",
        "com.mobfox",
        "com.mopub",
        "com.my.target.ads",
        "com.unity3d.ads",
        "com.verizon.ads",
        "com.sponsorpay",
        "com.tapjoy",
        "com.vpon",
        "com.vungle",
        "com.zendesk.sdk",
        "net.nend.android",
        "jp.maio.sdk",
        "jp.co.imobile",
    ])

    @staticmethod
    def process_packages(packages):
        return set(f"{LibraryExtractor.PREFIX}{dot_to_slash(pck)}" for pck in packages)

    @staticmethod
    def detected_packages(smali_file, packages):
        detected = set()
        with open(smali_file) as f:
            s = f.read()
            for package in packages:
                if package in s:
                    detected.add(package)
        return detected

    @staticmethod
    def is_smali_file(f):
        f_name = os.path.basename(f)
        return os.path.isfile(f) and f_name.endswith(SMALI_FILE_SUFFIX)

    @staticmethod
    def get_ad_tracking_libraries(target_apk, model_dir):
        result_file = os.path.join(model_dir, LibraryExtractor.RESULTS_FILE_NAME)

        detected_libraries = set()
        if os.path.isfile(result_file):
            # The results file exists already, so just read in and skip the processing
            with open(result_file, 'rb') as fp:
                detected_libraries = pickle.load(fp)
        else:
            # Results file doesn't exist yet, so process the apk

            # Check if the apktool output exists already
            output_dir = os.path.join(model_dir, APKTOOL_OUTPUT_DIR)
            if not os.path.isdir(output_dir):
                execute_cmd(f"java -jar {APKTOOL_PATH} d '{target_apk}' -o '{output_dir}'")

            libraries_to_check = LibraryExtractor.process_packages(LibraryExtractor.AD_TRACKING_LIBRARIES)

            for smali_resources_f in filter(lambda e: os.path.isdir(os.path.join(output_dir, e))
                                                      and e.startswith(SMALI_RES_DIR_PREFIX), os.listdir(output_dir)):
                smali_resources_dir = os.path.join(output_dir, smali_resources_f)
                # We have to ignore the folders from the blacklist
                res_dir_filter = filter(
                    lambda e: os.path.isdir(os.path.join(smali_resources_dir, e)) and e not in LibraryExtractor.BLACKLIST_SMALI_DIRS,
                    os.listdir(smali_resources_dir))
                for package_f in res_dir_filter:
                    package_dir = os.path.join(smali_resources_dir, package_f)
                    # From here we have to walk through and modify the files
                    for root, dirs, files in os.walk(package_dir):
                        for f_name in files:
                            smali_file = os.path.join(root, f_name)
                            if LibraryExtractor.is_smali_file(smali_file):
                                detected = LibraryExtractor.detected_packages(smali_file, libraries_to_check)
                                detected_libraries = detected_libraries.union(detected)
                                libraries_to_check = libraries_to_check.difference(detected)

            # Dump here detected libraries
            with open(result_file, 'wb') as f:
                pickle.dump(detected_libraries, f)

        return detected_libraries
