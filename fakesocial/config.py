"""
"""

import json


config = {
    "db_file": ":memory:",
    "number_of_events": 100,
    "output_dir": "site",
    "start_date": "2020-01-01",
}


def load_config_file(filepath):
    global config
    with open(filepath) as f:
        user_config = json.load(f)
    config = {
        **config,
        **user_config,
    }
