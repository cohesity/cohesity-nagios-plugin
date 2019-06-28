#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage :
# python check_cohesity_objects.py -i 'IP ADDRESS' -u 'USERNAME'
# -p 'PASSWORD' -d 'DOMAIN'
# check sources protected
# and returns a warning the protected sources exceeds 90%
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow the
# execution to 'all' (usually chmod 0755).
import argparse
import config
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityObjects(nagiosplugin.Resource):
    def __init__(self):
        """
        Method to initialize
        :param ip(str): ip address.
        :param user(str): username.
        :param password(str): password.
        :param domain(str): domain.
        """
        self.cohesity_client = CohesityClient(cluster_vip=config.ip,
                                              username=config.username,
                                              password=config.password,
                                              domain=config.domain)

    @property
    def name(self):
        return 'COHESITY_CLUSTER_OBJECTS_PROTECTED'

    def get_object(self):
        """
        Method to get the cohesity objects protected and not protected
        :return: list(lst): of protected and not protected
        """
        try:
            object_list = self.cohesity_client.protection_sources.\
                list_protection_sources_registration_info(
                    include_entity_permission_info=True)
        except APIException as e:
            _log.debug("APIException raised: " + e)
        protected = 0
        unprotected = 0
        stats = object_list.stats_by_env
        for r in stats:
            protected = r.protected_count + protected
            unprotected = r.unprotected_count + unprotected

        return [protected, unprotected]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        objects = self.get_object()
        total_protected = float(objects[0]) + float(objects[1])
        protected_objects = objects[0]
        percent_p = int(
            float(protected_objects) /
            float(total_protected) *
            100)
        _log.info("Percentage of sources protected {0} %".format(percent_p))
        metric = nagiosplugin.Metric(
            "Percentage of sources protected",
            percent_p,
            '%',
            min=0,
            max=100,
            context='protected')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default='~:90',
        help='return warning if occupancy is outside RANGE')
    argp.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='increase output verbosity (use up to 3 times)')
    argp.add_argument(
        '-t',
        '--timeout',
        default=30,
        help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        CohesityObjects())
    check.add(nagiosplugin.ScalarContext('protected', args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
