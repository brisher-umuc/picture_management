"""
return a dictionary of settings from settings.config

expects lines to be in the following format
setting=value

expects settings.config file to exist in the same directory
"""
#!/usr/bin/python2
from __future__ import print_function


def get_settings():
    with open('settings.config', 'r') as f:
        lines = [x.strip() for x in f.readlines()]

    dict_ = {}
    for line in lines:
        key, value = line.split('=')
        dict_[key] = value

    return dict_


if __name__ == '__main__':
    get_settings()