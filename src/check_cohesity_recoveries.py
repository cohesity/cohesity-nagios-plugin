#!/usr/bin/env python

# Copyright 2019 Cohesity Inc.


"""
check_cohesity_recoveries.py
This script looks recoveries in the last 30 day
if no recoveries returns OK status
if there are recoveries raises a warning

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


class Cohesityrecoveries(nagiosplugin.Resource):
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
        return 'cohesity_RECOVERY_STATUS'

    def get_recoveries(self):
        """
        Method to get the number of recoveries during the last 30 days
        :return: number of recoveries
        """
        try:
            recover = self.cohesity_client.dashboard
            number_recoveries = recover.get_dashboard()
            number = number_recoveries.dashboard.recoveries.last_month_num_recoveries
            if number == "None":
                number = 0
        except BaseException:
            _log.debug("Cohesity Cluster is not active")

        return number

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        number = self.get_recoveries()

        if number > 0:
            _log.info(
                'There are ' +
                str(number) +
                ' recoveries in the last 30 days')
        else:
            _log.info('No recoveries in the last 30 days')

        metric = nagiosplugin.Metric(
            'Alerts with issues', number, min=0, context='warning')
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
        help='return warning if occupancy is outside RANGE. Value is expressed in number of recoveries')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        Cohesityrecoveries(
            args.ip,
            args.user,
            args.password))
    check.add(nagiosplugin.ScalarContext('warning', args.warning))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
