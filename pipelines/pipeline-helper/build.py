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
    parser.add_argument('-s', '--stage',
                        required=True,
                        help='which stage do you want to execute?')
    return parser.parse_args()


def archive_and_upload():
    """
    generate a package and upload it to artifactory
    """
    logger.info('creating archive')
    archive = create_archive()
    archive = os.path.basename(archive)
    logger.info('uploading archive {0}'.format(archive))
    artifactory_config = read_configuration(DEFAULT_CONFIG_FILE, 'artifactory')
    username = artifactory_config['username']
    username = username.replace('$CI_PROJECT_NAME', os.environ['CI_PROJECT_NAME'])
    # pipeline.json contains the NAME of the variable
    # the actual password is stored within gitlab variables
    password = artifactory_config['password']
    password = gitlab_var(password, default='Not defined')
    for url in artifactory_urls():
        url = url.replace('$CI_PROJECT_NAME', os.environ['CI_PROJECT_NAME'])
        artifactory.upload(url=url,
                           username=username,
                           password=password,
                           file_to_upload=archive)


def main():
    args = parse_cli()
    stage = args.stage
    try:
        project_name = os.environ['CI_PROJECT_NAME']
    except KeyError:
        raise PipelineError('CI_PROJECT_NAME is not defilend')
    project_config = read_configuration(DEFAULT_CONFIG_FILE, 'build')
    steps = project_config[stage]['steps']

    for step in steps:
        logger.info('\nstep: {0}'.format(step))
        image_name = "{0}{1}".format(project_name,
                                     steps[step]['docker-image-suffix'])
        dockerfile = steps[step]['dockerfile']
        options = steps[step]['options']
        command = steps[step]['command']
        volumes = steps[step]['volumes']
        try:
            output = steps[step]['output']
        except KeyError:
            output = None
        docker.execute(image_name=image_name, dockerfile=dockerfile,
                       options=options, command=command, volumes=volumes,
                       output=output)

    # if this is the package stage, we need to create an archive with our
    # php dependencies, and upload it to artifactory
    if stage == 'package':
        archive_and_upload()

    docker.cleanup_volumes('/app')


if __name__ == '__main__':
    try:
        main()
    except PipelineError as error:
        logger.error(error)
        docker.cleanup_volumes('/app')
        sys.exit(-1)

