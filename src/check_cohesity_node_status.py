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

import datetime
import os
from cohesity_management_sdk.cohesity_client import CohesityClient
import argparse
from cohesity_management_sdk.models.alert_state_list_enum import AlertStateListEnum
from cohesity_management_sdk.models.alert_severity_list_enum import AlertSeverityListEnum
from cohesity_management_sdk.models.alert_category_list_enum import AlertCategoryListEnum
import argparse
import logging
import nagiosplugin
import urllib3


CLUSTER_USERNAME = 'admin'
CLUSTER_PASSWORD = 'admin'
CLUSTER_VIP = '10.2.148.30'
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
        self.password= password 
        self.cohesity_client = CohesityClient(cluster_vip= CLUSTER_VIP,
                                     username=CLUSTER_USERNAME,
                                     password=CLUSTER_PASSWORD,
                     domain=DOMAIN)
    @property
    def name(self):
        return 'cohesity_NODE_STATUS'
  
    def get_node_status(self):
        """
        Method to get the cohesity status if critical
        :return: alert_list1(lst): all the alerts that are critical for nodes
        """
        try: 
            alerts = self.cohesity_client.alerts
            alerts_list = alerts.get_alerts(alert_category_list=AlertCategoryListEnum.KNODEHEALTH, max_alerts=100,
                                        alert_state_list=AlertStateListEnum.KOPEN, alert_severity_list=AlertSeverityListEnum.KCRITICAL )
        except: 
            _log.debug("Cohesity Cluster is not active")
 
        return alerts_list
     

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        critical_node = self.get_node_status()

        critical = len(critical_node)
        bad_nodes = critical
        if bad_nodes == 0:
            _log.info('All ' + ' nodes are in a NON CRITICAL status')
        else:
            _log.debug(str(bad_nodes)+' returned an unhealthy status')

        metric = nagiosplugin.Metric('Unhealthy nodes', bad_nodes, min=0, context='bad_nodes')
        return metric


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--cohesity_client', help="cohesity ip address, username, and password")
    argp.add_argument('-i', '--ip', help="cohesity ip address")
    argp.add_argument('-u', '--user', help="cohesity username")
    argp.add_argument('-p', '--password', help="cohesity password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default='~:0', help='return warning if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='~:0', help='return critical if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()





@nagiosplugin.guarded
def main():


    args = parse_args()
    check = nagiosplugin.Check( Cohesitynodestatus(args.ip, args.user, args.password) )
    check.add(nagiosplugin.ScalarContext('bad_nodes', args.warning, args.critical))
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()