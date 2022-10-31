import os

from piscis.config.global_config import global_config as g
from piscis.config.yaml_config_loader import YamlConfigLoader

global_config = g
stage = os.environ.get("STAGE", "development")

CONF_FILE = os.path.join(os.path.dirname(__file__), f"{stage}.yaml")
global_config.settings = YamlConfigLoader(CONF_FILE)
