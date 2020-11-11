# -*- coding: utf-8 -*-
import os
import re


regex = re.compile(r"'traceId':'.{36}'", re.IGNORECASE)


def main():
    base_path = "./Data/run/exploration/playback1/model"
    for f in os.listdir(base_path):
        apk_model_dir = os.path.join(base_path, f)
        if os.path.isdir(apk_model_dir):
            for f1 in os.listdir(apk_model_dir):
                model_dir_f = os.path.join(apk_model_dir, f1)
                if model_dir_f.endswith(".har"):
                    custom_id = get_unique_id(f1)
                    print(model_dir_f, custom_id)
                    replace_in_file(model_dir_f, custom_id)


def replace_in_file(file, custom_id):
    """
    'traceId':'91986fde-36a0-4aa2-aaee-8ec55aeb7737'
    """
    custom_str = f"'traceId':'{custom_id}'"
    s = ""
    with open(file, "r") as f:
        for line in f:
            s += regex.sub(custom_str, line)

    with open(file, 'w') as f:
        f.write(s)


def get_unique_id(f: str):
    return f.replace(".har", "").replace("data", "")


if __name__ == '__main__':
    main()
