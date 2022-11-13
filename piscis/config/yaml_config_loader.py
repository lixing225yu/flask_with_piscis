import pyaml

from addict import Dict


class YamlConfigLoader:
    def __init__(self, conf_file):
        yaml = pyaml.yaml.safe_load(open(conf_file))
        self.yaml_dict = Dict(yaml)

    def __getattr__(self, item):
        return self.yaml_dict.get(item)

    def overlay(self, conf_file):
        yaml = pyaml.yaml.safe_load(open(conf_file))
        self.yaml_dict.update(Dict(yaml))
