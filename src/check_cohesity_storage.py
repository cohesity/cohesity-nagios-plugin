#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# This script is used to monitor percentage of total storage used
# used_capacity: The total capacity used, as computed by the Cohesity Cluster, after the size of the data has been
# reduced by change-block tracking, compression and deduplication
# total_capacity: The total physical capacity in bytes as computed by the Cohesity Cluster.
#                          used_capacity
#          percent used =  -------------- * 100
#                          total_capacity
#
# Usage :
# python check_cohesity_storage.py --cluster_vip 10.10.99.100 --host_name PaulCluster
#                                              --auth_file /abc/def/config.ini -w 60 -c 90
#


import argparse
import logging
import nagiosplugin
import configparser
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityClusterStorage(nagiosplugin.Resource):
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
        return 'COHESITY_CLUSTER_STORAGE'

    def get_cluster_storage(self):
        """
        Method to get the cohesity storage used and total storage available
        :return: list(lst): of available and used
        """
        try:
            cluster_info = self.cohesity_client.cluster.get_cluster(
                fetch_stats=True)
        except APIException as e:
            _log.debug("get cluster APIException raised: " + e)
        used_storage = cluster_info.stats.usage_perf_stats.\
            total_physical_usage_bytes
        total_storage = cluster_info.stats.usage_perf_stats.physical_capacity_bytes
        return [used_storage, total_storage]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        storage = self.get_cluster_storage()
        percent_used = int((float(storage[0]) / float(storage[1])) * 100)

        _log.info("Cluster ip = {}: ".format(self.args.cluster_vip) +
                  "Cluster storage is {0} % used".format(percent_used))
        metric = nagiosplugin.Metric(
            "Cluster used storage",
            percent_used,
            '%',
            min=0,
            max=100,
            context='cluster_used_storage')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-ip', '--cluster_vip', required=True,
                      help='Cohesity cluster ip or FQDN')
    argp.add_argument('-n', '--host_name', required=True,
                      help='Host name configured in Nagios')
    argp.add_argument('-f', '--auth_file', required=True,
                      help='.ini file path with Cohesity cluster credentials')
    argp.add_argument('-w', '--warning', metavar='RANGE', default='~:60', help='return warning'
                                                                               ' if occupancy is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='~:80', help='return critical if'
                                                                                ' occupancy is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output'
                                                                         ' verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        CohesityClusterStorage(args))
    check.add(
        nagiosplugin.ScalarContext(
            'cluster_used_storage',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
