#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# This script is used to find number of active nodes on a Cohesity cluster and status is
#  OK - if number of inactive nodes is zero
#  CRITICAL - if the number if inactive nodes is non zero
#
# Usage :
# python check_cohesity_node_status.py --cluster_vip 10.10.99.100 --host_name PaulCluster
#                                      --auth_file /abc/def/config.ini
#

import argparse
import json
import logging
import nagiosplugin
import requests
import configparser
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityNodeStatus(nagiosplugin.Resource):
    def __init__(self, args):
        """
        Method to initialize
        :param args: commandline arguments
        """
        parser = configparser.ConfigParser()
        parser.read(args.auth_file)
        self.args = args
        self.username = parser.get(args.host_name, 'username')
        self.password = parser.get(args.host_name, 'password')
        self.domain = parser.get(args.host_name, 'domain')

    @property
    def name(self):
        return 'COHESITY_NODE_STATUS'

    def get_node_status(self):
        """
        Method to get the cohesity node status
        :return: node_list(lst): number of total and active nodes
        """
        APIROOT = 'https://' + self.args.cluster_vip + '/irisservices/api/v1'
        creds = json.dumps({
            "domain": self.domain,
            "password": self.password,
            "username": self.username
        })
        HEADER = {
            'accept': 'application/json',
            'content-type': 'application/json'}
        url = APIROOT + '/public/accessTokens'
        try:
            response = requests.post(
                url, data=creds, headers=HEADER, verify=False)
        except APIException as e:
            _log.debug("post request APIException raised: " + e)
        if response != '':
            if response.status_code == 201:
                accessToken = response.json()['accessToken']
                tokenType = response.json()['tokenType']
                HEADER = {'accept': 'application/json',
                          'content-type': 'application/json',
                          'authorization': tokenType + ' ' + accessToken}
        try:
            response = requests.get(
                APIROOT +
                '/nexus/cluster/status',
                headers=HEADER,
                verify=False)
        except APIException as e:
            _log.debug("get cluster status APIException raised: " + e)
        response = response.json()
        node_stats = response["nodeStatus"]
        num_nodes = 0
        active_nodes = []
        for nodes in node_stats:
            num_nodes = num_nodes + 1
            active_nodes.append(0)
            if nodes['serviceStatus']:
                for service in nodes['serviceStatus']:
                    if len(service['processIds']) > 1:
                        active_nodes[num_nodes - 1] = 1
                        break
        return active_nodes

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        active_nodes = self.get_node_status()
        num_nodes = len(active_nodes)
        active_nodes = active_nodes.count(1)
        bad_nodes = num_nodes - active_nodes

        if num_nodes == active_nodes:
            _log.info("Cluster ip = {}: ".format(self.args.cluster_vip) +
                      "All {0} nodes are active".format(num_nodes))
        else:
            _log.info(
                "Cluster ip = {}: ".format(self.args.cluster_vip) +
                "{0} of {1} nodes active on cluster".format(active_nodes, num_nodes))

        metric = nagiosplugin.Metric(
            "Inactive nodes",
            bad_nodes,
            min=0,
            context='bad_nodes')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-ip', '--cluster_vip', required=True,
                      help='Cohesity cluster ip or FQDN')
    argp.add_argument('-n', '--host_name', required=True,
                      help='Host name configured in Nagios')
    argp.add_argument('-f', '--auth_file', required=True,
                      help='.ini file path with Cohesity cluster credentials')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity'
                                                                         ' (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        CohesityNodeStatus(args))
    check.add(nagiosplugin.ScalarContext('bad_nodes',
                                         critical='~:0'))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
