import yaml

from pathlib import Path


def load_config_as_dict(config_filename):
    config = yaml.safe_load(open(Path(__file__).absolute().parent.joinpath(config_filename)))
    return config
