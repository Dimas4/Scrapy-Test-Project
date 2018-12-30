import os

import yaml


def get_config():
    with open(os.path.join('config', 'config.yaml')) as file:
        config = yaml.load(file)
    return config
