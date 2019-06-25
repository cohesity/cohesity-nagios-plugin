#!/usr/bin/env python

# Copyright 2019 Cohesity Inc.

"""
check storage reduction of cohesity cluster

Info notifications 

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


class Cohesityclusterreduction(nagiosplugin.Resource):
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
        self.cohesity_client = CohesityClient(cluster_vip='10.2.148.30',
                                              username='admin',
                                              password='admin',
                                              domain=DOMAIN)

    @property
    def name(self):
        return 'cohesity_CLUSTER_DATA_REDUCTION'

    def get_cluster_reduction(self):
        """
        Method to get the cohesity reduction ratio
        :return: list(lst): ratio
        """
        try:
            cluster = self.cohesity_client.cluster
            cluster_stats = cluster.get_cluster(fetch_stats=True)
            reduction = cluster_stats.stats.data_reduction_ratio
        except BaseException:
            _log.debug("Cohesity Cluster is not active")

        return reduction

    def probe(self):
        """
        Method to get the status
        """
        ratio = int(self.get_cluster_reduction())

        _log.info('Cluster reduction ratio OK status ' + str(ratio))
        metric = nagiosplugin.Metric(
            'Reduction ratio',
            ratio,
            min=50,
            context='ratio')
        return metric

def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-s',
        '--cohesity_client',
        help="cohesity ip address, username, and password")
    argp.add_argument('-i', '--ip', help="Cohesity hostname or ip address")
    argp.add_argument('-u', '--user', help="Cohesity username")
    argp.add_argument('-p', '--password', help="Cohesity password")
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default='@0:50',
        help='return warning if occupancy is inside RANGE.')    
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        Cohesityclusterreduction(
            args.ip, args.user, args.password))
    check.add(nagiosplugin.ScalarContext('ratio',  args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
