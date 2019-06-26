#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage : 
# python check_cohesity_node_status.py -i 'IP ADDRESS' -u 'USERNAME' -p 'PASSWORD'
# This script lets the user know if any nodes are not active on cluster
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).
import argparse
import logging
import nagiosplugin
import requests
import json

from cohesity_management_sdk.cohesity_client import CohesityClient

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
        self.username = username
        self.password = password
        self.cohesity_client = CohesityClient(cluster_vip=ip,
                                              username=username,
                                              password=password,
                                              domain=DOMAIN)

    @property
    def name(self):
        return 'cohesity_NODE_STATUS'

    def get_node_status(self):
        """
        Method to get the cohesity node status
        :return: node_list(lst): number of total and active nodes
        """
        global APIROOT
        APIROOT = 'https://' + str(self.ip) + '/irisservices/api/v1'
        creds = json.dumps({
            "domain": str(DOMAIN),
            "password": str(self.password),
            "username": str(self.username)
        })
        global HEADER
        HEADER = {
            'accept': 'application/json',
            'content-type': 'application/json'}
        url = APIROOT + '/public/accessTokens'
        try:
            response = requests.post(
                url, data=creds, headers=HEADER, verify=False)
            if response != '':
                if response.status_code == 201:
                    accessToken = response.json()['accessToken']
                    tokenType = response.json()['tokenType']
                    HEADER = {'accept': 'application/json',
                              'content-type': 'application/json',
                              'authorization': tokenType + ' ' + accessToken}
                    global AUTHENTICATED
                    AUTHENTICATED = True
            response = requests.get(
                APIROOT +
                '/nexus/cluster/status',
                headers=HEADER,
                verify=False)
            response = response.json()
            node_stats = response["nodeStatus"]
            num_nodes = 0
            activity = []
            for nodes in node_stats:
                num_nodes = num_nodes + 1
                activity.append(0)
                for service in nodes["serviceStatus"]:
                    if len(service["processIds"]) > 1:
                        activity[num_nodes - 1] = 1
                        break
            return activity
        except BaseException:
            _log.debug("Cohesity Cluster is not active")

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        activity = self.get_node_status()
        num_nodes = len(activity)
        active = activity.count(1)
        bad_c = num_nodes - active

        if num_nodes == active:
            _log.info('All ' + str(num_nodes) + ' nodes active')
        else:
            _log.debug(
                str(active) +
                ' of ' +
                str(num_nodes) +
                ' active on cluster')

        metric = nagiosplugin.Metric(
            'Unactive node alerts',
            bad_c,
            min=0,
            context='bad_c')
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
        help='return warning if occupancy is outside RANGE.')
    argp.add_argument(
        '-c',
        '--critical',
        metavar='RANGE',
        default='~:0',
        help='return critical if occupancy is outside RANGE.')
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
    check.add(nagiosplugin.ScalarContext('bad_c', args.warning, args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
