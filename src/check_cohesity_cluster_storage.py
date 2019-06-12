#!/usr/bin/env python

# Copyright 2019 Cohesity Inc.

"""
check used metadata storage of cohesity cluster 

and returns a warning if the usage is over 60%, and a critical
alert if the usage is above 80%.

Requires the following non-core Python modules:
- nagiosplugin
- cohesity sdk 
user excecution rights to all

"""
import os
import argparse
import datetime
from cohesity_management_sdk.cohesity_client import CohesityClient
import argparse
import logging
import nagiosplugin
import urllib3


CLUSTER_USERNAME = 'admin'
CLUSTER_PASSWORD = 'admin'
CLUSTER_VIP = '10.2.148.30'
DOMAIN = 'LOCAL'
cohesity_client = CohesityClient(cluster_vip=CLUSTER_VIP,
                                     username=CLUSTER_USERNAME,
                                     password=CLUSTER_PASSWORD,
                     domain=DOMAIN)

_log = logging.getLogger('nagiosplugin')


class Cohesityclusterstorage(nagiosplugin.Resource):
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
        

    @property
    def name(self):
        return 'cohesity_CLUSTER_STORAGE'

    def get_cluster_storage(self):
        """
        Method to get the cohesity storage used and available
        :return: list(lst): of available and used 
        """
        try:
            alerts = cohesity_client.cluster
            alerts_list = alerts.get_cluster(fetch_stats= True)
            used = alerts_list.stats.usage_perf_stats.total_physical_usage_bytes
            total = alerts_list.stats.usage_perf_stats.physical_capacity_bytes
        except: 
            _log.debug("Cohesity Cluster is not active")
            
        return [used, total]


    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        storage = self.get_cluster_storage()
        percent_used = int((float(storage[0])/float(storage[1]))* 100)
        
        _log.info('Cluster storage is '+str(percent_used)+'% used')
        metric = nagiosplugin.Metric('Cluster used  storage', percent_used, '%', min=0, max=100, context='cluster_used')
        return metric

def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--cohesity_client', help="cohesity ip address, username, and password")
    argp.add_argument('-i', '--ip', help="Cohesity hostname or ip address")
    argp.add_argument('-u', '--user', help="Cohesity username")
    argp.add_argument('-p', '--password', help="Cohesity password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default=':60', help='return warning if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-c', '--critical', metavar='RANGE', default=':80', help='return critical if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()

@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check( Cohesityclusterstorage(args.ip, args.user, args.password) )
    check.add(nagiosplugin.ScalarContext('cluster_used', args.warning, args.critical))
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()