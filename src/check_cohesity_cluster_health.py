#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage :
# python check_cohesity_cluster_health.py -i 'IP ADDRESS' -u
# 'USERNAME' -p 'PASSWORD' -d 'DOMAIN'
# This script lets the user know if the cluster is healthy or not,
# if there are no warnings or critical status'
# an OK status is returned
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow the execution
# to 'all' (usually chmod 0755).
import argparse
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.models.alert_state_list_enum import (
    AlertStateListEnum)
from cohesity_management_sdk.models.alert_category_list_enum import (
    AlertCategoryListEnum)
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.alert_severity_list_enum import (
    AlertSeverityListEnum)

_log = logging.getLogger('nagiosplugin')


class CohesityClusterHealth(nagiosplugin.Resource):
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
        return 'COHESITY_CLUSTER_HEALTH'

    def get_cluster_status(self):
        """
        Method to get the cohesity status if critical
        :return: alert_list1(lst): all the alerts that are critical
        or warning for cluster
        """
        try:
            alerts_list = self.cohesity_client.alerts.get_alerts(
                alert_category_list=AlertCategoryListEnum.KCLUSTERHEALTH,
                max_alerts=100,
                alert_state_list=AlertStateListEnum.KOPEN)
        except APIException as e:
            _log.debug("APIException raised: " + e)
        alerts_list1 = []
        for r in alerts_list:
            if r.alert_severity == (
                AlertSeverityListEnum.KCRITICAL or
                    AlertSeverityListEnum.KWARNING):
                r.append(alerts_list1)
        return alerts_list1

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        not_healthy_lst = self.get_cluster_status()

        non_healthy_num = len(not_healthy_lst)
        if non_healthy_num == 0:
            _log.info("Cluster is in an OK status")
        else:
            _log.debug("{0} alerts returned an unhealthy" +
                       " status".format(non_healthy_num))

        metric = nagiosplugin.Metric(
            "Unhealthy cluster alerts",
            non_healthy_num,
            min=0,
            context='non_healthy_num')
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
        CohesityClusterHealth(
            args.ip,
            args.user,
            args.password,
            args.domain))
    check.add(
        nagiosplugin.ScalarContext('non_healthy_num',
                                   args.warning, args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
