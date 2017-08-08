#!/usr/bin/env python
"""
QA approvals
"""

from __future__ import print_function
from __future__ import absolute_import
import argparse
import os
import sys
import lib.kerberos as kerberos
from lib.error import PipelineError
from lib.utils import SUCCESS, FAILED, read_configuration, DEFAULT_CONFIG_FILE


# some constants...
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def signoff(config_file, environment):
    """
    The only function you want to call from main(). A nice cozy wrapper for the
    singoff operations, nothing more, nothing less.

    Args:
        config_file (str): path to the configuration file
        environment (str): the environment you're about to deploy
    """
    config = read_configuration(config_file=config_file, environment=environment)
    user = kerberos.current_user_email()
    try:
        kerberos.check(config)
    except PipelineError as error:
        raise PipelineError(error)
    # user is authorized to trigger this job
    print('{0} signed off by: {1}'.format(SUCCESS, environment, user))


def main():
    """
    I am main(), I do sign offs on behalf of QA
    """
    parser = argparse.ArgumentParser("signoff script")
    parser.add_argument('--environment', '-e', help='environment to deploy',
                        required=True)
    parser.add_argument('--config-file', '-c',
                        help='configuration file, defaults to: {0}'.format(
                            DEFAULT_CONFIG_FILE),
                        default=DEFAULT_CONFIG_FILE,
                        required=False)
    args = parser.parse_args()
    try:
        signoff(config_file=args.config_file, environment=args.environment)
    except PipelineError as error:
        print(error)
        sys.exit(1)

if __name__ == '__main__':
    main()

