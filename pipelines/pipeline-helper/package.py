#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import argparse
import os
import sys

import lib.artifactory as artifactory
import lib.docker as docker
from lib.error import PipelineError
from lib.logger import logger
from lib.utils import gitlab_var, create_archive, read_configuration
from lib.utils import artifactory_urls, DEFAULT_CONFIG_FILE


def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configuration-file',
                        required=True,
                        help='configuration file')
    return parser.parse_args()


def main():
    """
    generate a package and upload it to artifactory
    """
    logger.info('creating archive')
    args = parse_cli()
    package_config = read_configuration(args.configuration_file)
    archive = create_archive(package_config)
    archive = os.path.basename(archive)
    logger.info('uploading archive {0}'.format(archive))
    config = read_configuration(DEFAULT_CONFIG_FILE)
    artifactory_config = config['artifactory']
    username = artifactory_config['username']
    username = username.replace('$CI_PROJECT_NAME', os.environ['CI_PROJECT_NAME'])
    # pipeline.json contains the NAME of the variable
    # the actual password is stored within gitlab variables
    password = artifactory_config['password']
    password = password.replace('$ARTIFACTORY_PASSWORD', os.environ['ARTIFACTORY_PASSWORD'])

    if password == 'Not defined':
        logger.warning('no password defined for artifactory')
    for url in artifactory_urls():
        url = url.replace('$CI_PROJECT_NAME', os.environ['CI_PROJECT_NAME'])
        artifactory.upload(url=url,
                           username=username,
                           password=password,
                           file_to_upload=archive)



if __name__ == '__main__':
    try:
        main()
    except PipelineError as error:
        logger.error(error)
        docker.cleanup_volumes('/app')
        sys.exit(-1)

