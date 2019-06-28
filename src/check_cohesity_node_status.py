#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage :
# python check_cohesity_node_status.py
# This script lets the user know if any nodes are not active on cluster
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow
# the execution to 'all' (usually chmod 0755).
import argparse
import config
import json
import logging
import nagiosplugin
import requests

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException

_log = logging.getLogger('nagiosplugin')


class CohesityNodeStatus(nagiosplugin.Resource):
    def __init__(self):
        """
        Method to initialize
        :param ip(str): ip address.
        :param user(str): username.
        :param password(str): password.
        :param domain(str): domain.
        """
        self.ip = config.ip
        self.user = config.username
        self.password = config.password
        self.domain = config.domain

    @property
    def name(self):
        return 'COHESITY_NODE_STATUS'

    def get_node_status(self):
        """
        Method to get the cohesity node status
        :return: node_list(lst): number of total and active nodes
        """
        APIROOT = 'https://' + self.ip + '/irisservices/api/v1'
        creds = json.dumps({
            "domain": self.domain,
            "password": self.password,
            "username": self.user
        })
        HEADER = {
            'accept': 'application/json',
            'content-type': 'application/json'}
        url = APIROOT + '/public/accessTokens'
        try:
            response = requests.post(
                url, data=creds, headers=HEADER, verify=False)
        except APIException as e:
            _log.debug("APIException raised: " + e)
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
            _log.debug("APIException raised: " + e)
        response = response.json()
        node_stats = response["nodeStatus"]
        num_nodes = 0
        activity = []
        for nodes in node_stats:
            num_nodes = num_nodes + 1
            activity.append(0)
            for service in nodes['serviceStatus']:
                if len(service['processIds']) > 1:
                    activity[num_nodes - 1] = 1
                    break
        return activity

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        activity = self.get_node_status()
        num_nodes = len(activity)
        active = activity.count(1)
        bad_nodes = num_nodes - active

        if num_nodes == active:
            _log.info("All {0} nodes active".format(num_nodes))
        else:
            _log.debug(
                "{0} of {1} active on cluster".format(active, num_nodes))

        metric = nagiosplugin.Metric(
            "Unactive nodes are/",
            bad_nodes,
            min=0,
            context='bad_nodes')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-w',
        '--warning',
        metavar='RANGE',
        default='~:0',
        help='return warning if occupancy is outside RANGE')
    argp.add_argument(
        '-c',
        '--critical',
        metavar='RANGE',
        default='~:0',
        help='return critical if occupancy is outside RANGE')
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
        CohesityNodeStatus())
    check.add(nagiosplugin.ScalarContext('bad_nodes',
                                         args.warning, args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
