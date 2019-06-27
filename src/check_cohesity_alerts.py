#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage :
# python check_cohesity_alerts.py
# This script looks at alerts and raises an alert for
# Alert status of type: warnings or severe status'
# else if just info everything is OK for the last day, max 1000 alerts
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow
# the execution to 'all' (usually chmod 0755).
import argparse
import datetime
import logging
import nagiosplugin
import config

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.models.alert_state_list_enum import (
                                                AlertStateListEnum)
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.alert_severity_list_enum import (
                                                AlertSeverityListEnum)


_log = logging.getLogger('nagiosplugin')


class CohesityAlerts(nagiosplugin.Resource):
    def __init__(self):
        """
        Method to initialize
        :param ip(str): ip address.
        :param user(str): username.
        :param password(str): password.
        :param domain(str): domain.
        """
        self.cohesity_client = CohesityClient(cluster_vip=config.ip,
                                              username=config.username,
                                              password=config.password,
                                              domain=config.domain)

    @property
    def name(self):
        return 'COHESITY_ALERT_STATUS'

    def get_alerts(self):
        """
        Method to get the cohesity status if critical
        :return: alert_list(lst): all the alerts that are critical or warnings
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        end = datetime.datetime.utcnow()
        end_date = int((end - epoch).total_seconds()) * 1000000
        start = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        start_date = int((start - epoch).total_seconds()) * 1000000
        try:
            alerts_list = self.cohesity_client.alerts.get_alerts(
                start_date_usecs=start_date, end_date_usecs=end_date,
                max_alerts=1000, alert_state_list=AlertStateListEnum.KOPEN)
        except APIException as e:
            _log.debug("APIException raised: " + e)

        alerts_list1 = []
        alerts_list2 = []
        for r in alerts_list:
            if r.severity == AlertSeverityListEnum.KCRITICAL:
                alerts_list1.append('critical')
            if r.severity == AlertSeverityListEnum.KWARNING:
                alerts_list2.append('warning')
        critical = len(alerts_list1)
        warning = len(alerts_list2)
        return [critical, warning]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        size = self.get_alerts()
        critical = size[0]
        warning = size[1]
        combined = critical + warning

        if critical > 0 or warning > 0:
            _log.debug(
                "There are {0} alerts in critical status and {1} " +
                "alerts in warning status in the past" +
                "day".format(critical, warning))
        else:
            _log.info(
                "All alerts are in info status or no alerts" +
                " exist in the past day")

        metric = nagiosplugin.Metric(
            "Alerts with issues",
            combined,
            min=0,
            context='warning/critical')
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
        CohesityAlerts())
    check.add(
        nagiosplugin.ScalarContext(
            'warning/critical',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
