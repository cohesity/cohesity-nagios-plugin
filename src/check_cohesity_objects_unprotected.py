#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# This script is used to monitor the percentage of unprotected objects on Cohesity cluster. Ths status is
#     OK - if the percentage of unprotected objects are within the warning threshold
#     WARNING -if the percentage of unprotected objects are is above the warning threshold
# The default warning threshold is 90
# Usage :
# python check_cohesity_objects_unprotected.py --cluster_vip 10.10.99.100 --host_name PaulCluster
#                                              --auth_file /abc/def/config.ini -w 60
#


import argparse
import logging
import nagiosplugin
import configparser
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityObjects(nagiosplugin.Resource):
    def __init__(self, args):
        """
        Method to initialize
        :param args: commandline arguments
        """
        parser = configparser.ConfigParser()
        parser.read(args.auth_file)
        self.cohesity_client = CohesityClient(cluster_vip=args.cluster_vip,
                                              username=parser.get(
                                                  args.host_name, 'username'),
                                              password=parser.get(
                                                  args.host_name, 'password'),
                                              domain=parser.get(args.host_name, 'domain'))
        self.args = args

    @property
    def name(self):
        return 'COHESITY_CLUSTER_OBJECTS_UNPROTECTED'

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
            _log.debug("get protection sources APIException raised: " + e)
        protected = 0
        unprotected = 0
        stats = object_list.stats_by_env
        if stats:
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
        unprotected_objects = objects[1]
        if not total_protected == 0:
            percent_unprotected = int(
                float(unprotected_objects) /
                float(total_protected) *
                100)
        else:
            percent_unprotected = 0
        _log.info("Cluster ip = {}: ".format(self.args.cluster_vip) +
                  "Percentage of sources unprotected {0} %".format(percent_unprotected))
        metric = nagiosplugin.Metric(
            "Percentage of sources unprotected",
            percent_unprotected,
            '%',
            min=0,
            max=100,
            context='unprotected')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-ip', '--cluster_vip', required=True,
                      help='Cohesity cluster ip or FQDN')
    argp.add_argument('-n', '--host_name', required=True,
                      help='Host name configured in Nagios')
    argp.add_argument('-f', '--auth_file', required=True,
                      help='.ini file path with Cohesity cluster credentials')
    argp.add_argument('-w', '--warning', metavar='RANGE', default='~:90', help='return warning if'
                                                                               ' occupancy is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity'
                                                                         ' (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        CohesityObjects(args))
    check.add(nagiosplugin.ScalarContext('unprotected', args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
