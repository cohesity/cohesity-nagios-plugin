#!/usr/bin/env python

# Copyright 2019 Cohesity Inc.

"""
check sources protected

and returns a warning the protected sources exceeds 90%

Requires the following non-core Python modules:
- nagiosplugin
- cohesity sdk
user excecution rights to all

"""
from cohesity_management_sdk.cohesity_client import CohesityClient
import argparse
import logging
import nagiosplugin

DOMAIN = 'LOCAL'

_log = logging.getLogger('nagiosplugin')


class Cohesityobjects(nagiosplugin.Resource):
    def __init__(self, ip, user, password):
        """
        Method to initialize
        :param ip(str): ip address.
        :param user(str): username.
        :param password(str): password.
        """
        self.ip = ip
        self.user = user
        self.password = password
        self.cohesity_client = CohesityClient(cluster_vip=ip,
                                              username=user,
                                              password=password,
                                              domain=DOMAIN)

    @property
    def name(self):
        return 'cohesity_CLUSTER_OBJECTS_PROTECTED'

    def get_object(self):
        """
        Method to get the cohesity objects protected and not protected
        :return: list(lst): of protected and not protected
        """
        try:
            objects = self.cohesity_client.protection_sources
            object_list = objects.list_protection_sources_registration_info(include_entity_permission_info=True)
            protected = 0
            notprotected = 0
            stats = object_list.stats_by_env 
            for r in stats: 
                protected = r.protected_count + protected 
                notprotected = r.unprotected_count + notprotected

        except BaseException:
            _log.debug("Cohesity Cluster is not active")
        return [protected, notprotected]

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
        _log.info('Percentage of sources protected ' + str(percent_p) + '%')
        metric = nagiosplugin.Metric(
            'Percentage of sources protected',
            percent_p,
            '%',
            min=0,
            max=100,
            context='protected')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-s',
        '--cohesity_client',
        help="Cohesity ip address, username, and password")
    argp.add_argument('-i', '--ip', help="Cohesity hostname or ip address")
    argp.add_argument('-u', '--user', help="Cohesity username")
    argp.add_argument('-p', '--password', help="Cohesity password")
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default=':90',
        help='return warning if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        Cohesityobjects(
            args.ip,
            args.user,
            args.password))
    check.add(nagiosplugin.ScalarContext('protected', args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
