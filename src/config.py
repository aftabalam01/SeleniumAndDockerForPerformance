import os
import os.path as path

import yaml

class Config(object):
    def __init__(self):
        with open("./config/config.yml", 'r') as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

CONFIG=Config().config
