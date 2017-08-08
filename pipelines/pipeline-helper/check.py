#!/usr/bin/env python

"""
This module takes care of your deploy.json
"""

from __future__ import print_function
from __future__ import absolute_import
import argparse
import os
import json
from lib.logger import logger


class Config:
    def __init__(self, configuration_file):
        self.configuration_file = os.path.abspath(configuration_file)
        data = open(self.configuration_file, 'r').read()
        data = json.loads(data)
        self.__dict__.update(data)

    def deploy_environments(self):
        """
        returns the list of enviroments
        """
        for key in self.deploy:
                yield key

    def keys(self):
        for key in self.__dict__:
            if key != 'configuration_file':
                yield key

    def build_stages(self):
        for key in self.build:
            if 'steps' in self.build[key]:
                for item in self.build[key]['steps']:
                    yield "{0}::{1}".format(key, item)

    def __str__(self):
        return self.configuration_file


def parse_cli():
    parser = argparse.ArgumentParser("Parse deploy.json as a pro")
    parser.add_argument('-c', '--configuration-file', help="configuration file",
                        required=True)
    return parser.parse_args()


def main():
    args = parse_cli()
    config = args.configuration_file
    config = Config(configuration_file=args.configuration_file)
    logger.info(config)
    logger.info('build stages: (stage::step)')
    for stage in config.build_stages():
        logger.info(' * {0}'.format(stage))

    logger.info('deployment environments')
    for env in config.deploy_environments():
        logger.info(' * {0}'.format(env))


if __name__ == '__main__':
    main()
