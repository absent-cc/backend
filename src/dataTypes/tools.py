# .ini reader
from configparser import ConfigParser

def config_parser(config_file):
    config = ConfigParser()
    config.read(config_file)
    return config

def write_config(config_file, section, key, value):
    config = config_parser(config_file)
    config[section][key] = value
    with open(config_file, 'w') as config_file:
        config.write(config_file)

def read_config(config_file, section, key):
    config = config_parser(config_file)
    return config[section][key]