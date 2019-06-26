#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <your_email_id>
# Usage : 
# python check_cohesity_alerts.py -i 'IP ADDRESS' -u 'USERNAME' -p 'PASSWORD'
# This script looks at alerts and raises an alert for Alert status of type: warnings or severe status'
# else if just info everything is OK for the last day, max 1000 alerts
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).
import argparse
import datetime
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.models.alert_state_list_enum import AlertStateListEnum

DOMAIN = 'LOCAL'


_log = logging.getLogger('nagiosplugin')


class Cohesityalerts(nagiosplugin.Resource):
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
        return 'cohesity_ALERT_STATUS'

    def get_alerts(self):
        """
        Method to get the cohesity status if critical
        :return: alert_list(lst): all the alerts that are critical or warnings
        """
        try:
            epoch = datetime.datetime.utcfromtimestamp(0)
            end = datetime.datetime.utcnow()
            end_date = int((end - epoch).total_seconds()) * 1000000
            start = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            start_date = int((start - epoch).total_seconds()) * 1000000
            alerts_list = self.cohesity_client.alerts.get_alerts(
                start_date_usecs=start_date, end_date_usecs=end_date,
                max_alerts=1000, alert_state_list=AlertStateListEnum.KOPEN)
        except BaseException:
            _log.debug("Cohesity Cluster is not active")

        alerts_list1 = []
        alerts_list2 = []
        for r in alerts_list:
            if r.severity == "kCritical":
                alerts_list1.append("critical")
            if r.severity == "kWarning":
                alerts_list2.append("warning")
        cc = len(alerts_list1)
        ww = len(alerts_list2)
        return [cc, ww]

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
                'There are ' +
                str(critical) +
                ' alerts in critical status and ' +
                str(warning) +
                ' alerts in warning status in the past day')
        else:
            _log.info(
                'All alerts are in info status or no alerts exist in the past day')

        metric = nagiosplugin.Metric(
            'Alerts with issues',
            combined,
            min=0,
            context='warning/critical')
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
        help='return warning if occupancy is outside RANGE')
    argp.add_argument(
        '-c',
        '--critical',
        metavar='RANGE',
        default='~:0',
        help='return critical if occupancy is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        Cohesityalerts(
            args.ip,
            args.user,
            args.password))
    check.add(
        nagiosplugin.ScalarContext(
            'warning/critical',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
