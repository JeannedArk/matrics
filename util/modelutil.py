# -*- coding: utf-8 -*-
import csv

import usecasemapping


def get_csv_dict_reader(f):
    """
    Handles the following case:
        1b18afdf-a3c9-34da-8c7a-717a77f0e275_5c4dd5a3-8ebe-3457-84bf-008722278f43;android.view.View;";BLA
    The double quote triggered a bug in parsing the csv file.
    """
    return csv.DictReader(f, delimiter=';', quoting=csv.QUOTE_NONE)


def get_csv_writer(f, fieldnames):
    # quotechar='"'
    return csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_MINIMAL)


USE_CASE_STATE_COMPUTED = "COMPUTED"
USE_CASE_STATE_VERIFIED = "VERIFIED"
USE_CASE_STATE_DEFINED_FOR_APP = "DEFINED"


def calculate_use_case_matrix(apps, model):
    use_cases = [use_case for use_case in model.use_case_manager.get_use_cases()]

    d = {}
    for app in apps:
        app_d = {}
        use_case_set_for_app = usecasemapping.APP_USE_CASE_MAP[app.package_name]
        use_case_set_verified = set(uce.use_case.name for uce in app.exploration_model.use_case_execution_manager.get_verified_use_case_executions())
        use_case_set_computed = set(uce.use_case.name for uce in app.exploration_model.use_case_execution_manager.get_computed_use_case_executions())
        for use_case in use_cases:
            app_use_case_d = {}
            # assert app.exploration_model.use_case_execution_manager.has_use_case(use_case=use_case, ignore_playback_state=True)
            use_case_defined_for_app = use_case.name in use_case_set_for_app
            app_use_case_d[USE_CASE_STATE_DEFINED_FOR_APP] = use_case_defined_for_app
            use_case_computed = use_case.name in use_case_set_computed
            app_use_case_d[USE_CASE_STATE_COMPUTED] = use_case_computed
            use_case_verified = use_case_defined_for_app and (use_case.name in use_case_set_verified)
            app_use_case_d[USE_CASE_STATE_VERIFIED] = use_case_verified
            app_d[use_case.name] = app_use_case_d

        d[app.package_name] = app_d

    return d
