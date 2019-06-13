#!/usr/bin/env python

# Copyright 2019 Cohesity Inc.


"""
check_cohesity_node_status.py
This script lets the user know if any nodes are in a critical status,
and returns a critical alert if any node has a status other than
NONCRITICAL.
Requires the following non-core Python modules:
- nagiosplugin
- cohesity/app-sdk-python

Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).
Created by Christina Mudarth
"""
from cohesity_management_sdk.cohesity_client import CohesityClient
import argparse
import logging
import nagiosplugin

DOMAIN = 'LOCAL'


_log = logging.getLogger('nagiosplugin')


class Cohesitynodestatus(nagiosplugin.Resource):
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
        return 'cohesity_NODE_STATUS'

    def get_node_status(self):
        """
        Method to get the cohesity status if critical
        :return: alert_list1(lst): all the alerts that are critical for nodes
        """
        counter = 0
        try:
            nodes = self.cohesity_client.nodes
            nodes_list = nodes.get_nodes()
            for num in nodes_list:
                counter = counter + 1
            nodes_cluster = self.cohesity_client.cluster
            cnodes = nodes_cluster.get_cluster()
            number_cluster = cnodes.node_count

        except BaseException:
            _log.debug("Cohesity Cluster is not active")
        return [counter, number_cluster]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        countt_node = self.get_node_status()
        difference = countt_node[0] - countt_node[1]
        if countt_node[0] == countt_node[1]:
            _log.info('All ' +
                      str(countt_node[0]) +
                      ' nodes are active on the cluster')
        else:
            _log.debug(str(difference) + ' nodes are not active on cluster')

        metric = nagiosplugin.Metric(
            'Unhealthy nodes',
            difference,
            min=0,
            context='difference')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-s',
        '--cohesity_client',
        help="cohesity ip address, username, and password")
    argp.add_argument('-i', '--ip', help="cohesity ip address")
    argp.add_argument('-u', '--user', help="cohesity username")
    argp.add_argument('-p', '--password', help="cohesity password")
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default='~:0',
        help='return warning if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument(
        '-c',
        '--critical',
        metavar='RANGE',
        default='~:0',
        help='return critical if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        Cohesitynodestatus(
            args.ip,
            args.user,
            args.password))
    check.add(
        nagiosplugin.ScalarContext(
            'difference',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
