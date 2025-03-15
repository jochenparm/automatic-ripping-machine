#!/usr/bin/python3
"""yaml config loader"""
from __future__ import annotations

import json
import os

import yaml

import fadr.config.config_utils as config_utils

CONFIG_LOCATION = "/etc/fadr/config"
fadr_config_path = os.path.join(CONFIG_LOCATION, "fadr.yaml")
abcde_config_path = os.path.join(CONFIG_LOCATION, "abcde.conf")
apprise_config_path = os.path.join(CONFIG_LOCATION, "apprise.yaml")


def _load_config(fp):
    with open(fp) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def _load_abcde(fp):
    with open(fp) as abcde_read_file:
        config = abcde_read_file.read()
    return config


# fadr config, open and read yaml contents
# handle fadr.yaml migration here
# 1. Load both current and template fadr.yaml
cur_cfg = _load_config(fadr_config_path)
new_cfg = _load_config("/opt/fadr/setup/fadr.yaml")

# 2. If the dicts do not have the same number of keys
if len(cur_cfg) != len(new_cfg):
    # 3. Update new dict with current values
    for key in cur_cfg:
        if key in new_cfg:
            new_cfg[key] = cur_cfg[key]

    # 4. Save the dictionary
    with open("/opt/fadr/fadr/ui/comments.json") as comments_file:
        comments = json.load(comments_file)

    fadr_cfg = comments['FADR_CFG_GROUPS']['BEGIN'] + "\n\n"
    for key, value in dict(new_cfg).items():
        # Add any grouping comments
        fadr_cfg += config_utils.fadr_yaml_check_groups(comments, key)
        # Check for comments for this key in comments.json, add them if they exist
        try:
            fadr_cfg += "\n" + comments[str(key)] + "\n" if comments[str(key)] != "" else ""
        except KeyError:
            fadr_cfg += "\n"
        # test if key value is an int
        value = str(value)  # just change the type to keep things as expected
        try:
            post_value = int(value)
            fadr_cfg += f"{key}: {post_value}\n"
        except ValueError:
            # Test if value is Boolean
            fadr_cfg += config_utils.fadr_yaml_test_bool(key, value)

    # this handles the truncation
    with open(fadr_config_path, "w") as settings_file:
        settings_file.write(fadr_cfg)
        settings_file.close()

fadr_config = _load_config(fadr_config_path)

# abcde config file, open and read contents
abcde_config = _load_abcde(abcde_config_path)

# apprise config, open and read yaml contents
apprise_config = _load_config(apprise_config_path)
