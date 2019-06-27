#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage :
# python check_cohesity_reduction.py -i 'IP ADDRESS'
# -u 'USERNAME' -p 'PASSWORD' -d 'DOMAIN'
# check storage reduction of cohesity cluster
# Info notifications
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to
# allow the execution to 'all' (usually chmod 0755).
import argparse
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityClusterReduction(nagiosplugin.Resource):
    def __init__(self, ip, user, password, domain):
        """
        Method to initialize
        :param ip(str): ip address.
        :param user(str): username.
        :param password(str): password.
        :param domain(str): domain.
        """
        self.cohesity_client = CohesityClient(cluster_vip=ip,
                                              username=user,
                                              password=password,
                                              domain=domain)

    @property
    def name(self):
        return 'COHESITY_CLUSTER_DATA_REDUCTION'

    def get_cluster_reduction(self):
        """
        Method to get the cohesity reduction ratio
        :return: list(lst): ratio
        """
        try:
            cluster_stats = self.cohesity_client.cluster.\
                get_cluster(fetch_stats=True)
            reduction = cluster_stats.stats.data_reduction_ratio
        except APIException as e:
            _log.debug("APIException raised: " + e)

        return reduction

    def probe(self):
        """
        Method to get the status
        """
        ratio = int(self.get_cluster_reduction())

        _log.info("Cluster reduction ratio OK status {0}".format(ratio))
        metric = nagiosplugin.Metric(
            "Reduction ratio",
            ratio,
            min=50,
            context='ratio')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-s',
        '--Cohesity_client',
        help="Cohesity ip address, username, and password")
    argp.add_argument(
        '-i',
        '--ip',
        help="Cohesity ip address")
    argp.add_argument(
        '-u',
        '--user',
        help="Cohesity username")
    argp.add_argument(
        '-p',
        '--password',
        help="Cohesity password")
    argp.add_argument(
        '-d',
        '--domain',
        help="Cohesity domain")
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default='~:0',
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
        CohesityClusterReduction(
            args.ip,
            args.user,
            args.password,
            args.domain))
    check.add(nagiosplugin.ScalarContext('ratio', args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
