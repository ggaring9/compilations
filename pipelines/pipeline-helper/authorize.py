#!/usr/bin/env python
"""
Very basic authorization mechanism.

It checks if the current user is part of the list of authorized users.
Later this module will be extended to use LDAP/AD authentication
"""

import os
import sys
from lib.logger import logger


def is_user_authorized():
    authorized_users = os.environ['AUTHORIZED_USERS'].split(',')
    user = os.environ['USER']
    if 'any' in authorized_users:
        logger.info('authorization: any user can execute this step')
        return True
    if user in authorized_users:
        logger.info('user: %s is part of the authorized users', user)
        return True
    logger.error('%s is not authorized to execute this stage', user)
    return False


def are_requirements_met():
    if 'DEPENDS_ON' not in os.environ:
        return True
    for dependency in os.environ['DEPENDS_ON'].split(','):
        if not os.path.exists(dependency):
            msg = ('dependencies are not met: this stage depends on {0} '
                   'but {0} does not exist. '.format(dependency))
            logger.error(msg)
            return False
    return True


def main():
    if not is_user_authorized():
        logger.error('you cannot execute this stage.')
        sys.exit(1)
    if not are_requirements_met():
        logger.error('dependencies are not met.')
        sys.exit(1)
    logger.info('this stage can be executed')


if __name__ == '__main__':
    try:
        main()
    except KeyError as error:
        logger.error('missing key in your environment: %s', error)
        logger.error('your journey ends here, my friend')
        sys.exit(1)

