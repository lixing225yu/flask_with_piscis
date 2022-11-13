import os

from piscis.config.global_config import global_config
from piscis.config.yaml_config_loader import YamlConfigLoader

for stage in ['production']:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'.env.{stage}')
    if os.path.exists(path):
        break
else:
    stage = 'development'
print(f'current stage is: {stage}')

common_conf_file = os.path.join(os.path.dirname(__file__), "common.yaml")
global_config.settings = YamlConfigLoader(common_conf_file)
env_file = os.path.join(os.path.dirname(__file__), f"{stage}.yaml")
global_config.settings.overlay(env_file)
settings = global_config.settings
