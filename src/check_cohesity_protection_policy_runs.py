#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# Usage : 
# python check_cohesity_protection_policy_runs.py -i 'IP ADDRESS' -u 'USERNAME' -p 'PASSWORD'
# This script looks at protection runs in the past days that have passed. succesfully
# if all passed it is OK
# else raise a warning
# Requires the following non-core Python modules:
# - nagiosplugin
# - cohesity_management_sdk
# Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).
import argparse
import datetime
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient

_log = logging.getLogger('nagiosplugin')


class Cohesityprotectionstatus(nagiosplugin.Resource):
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
        return 'cohesity_PROTECTION_RUN_STATUS'

    def get_protection_status(self):
        """
        Method to get the protection run status
        :return: number of passed and failed protection runs
        """
        try:
            protection_runs_list = self.cohesity_client.protection_runs.get_protection_runs()
        except BaseException:
            _log.debug("Cohesity Cluster is not active")

        today = datetime.datetime.now()
        margin = datetime.timedelta(days=1)
        listt = []
        notnum = 0

        for protection_runs in protection_runs_list:
            try:
                if protection_runs.backup_run.status != "kFailure":
                    if today - margin <= self.epoch_to_date(
                            protection_runs.backup_run.stats.end_time_usecs) <= today + margin:
                        listt.append(protection_runs.job_name)
                elif today - margin <= self.epoch_to_date(protection_runs.backup_run.stats.end_time_usecs) <= today + margin:
                    notnum = 1 + notnum
            except TypeError as e:
                print ("")
        for protection_runs in protection_runs_list:
            try:
                if protection_runs.copy_run[0].status != "kFailure":
                    if today - margin <= self.epoch_to_date(
                            protection_runs.copy_run[0].run_start_time_usecs) <= today + margin:
                        listt.append(protection_runs.job_name)
                elif today - margin <= self.epoch_to_date(protection_runs.copy_run[0].run_start_time_usecs) <= today + margin:
                    notnum = 1 + notnum
            except TypeError as e:
                print ("")

        num = len(listt)
        return [num, notnum]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        protection = self.get_protection_status()
        succesfully = protection[0]
        fail = protection[1]

        if fail == 0:
            _log.info(
                'All ' +
                str(succesfully) +
                ' protection runs (backup + copy run) are not in failure status')
        else:
            _log.debug(
                str(fail) +
                ' protection runs have failed and ' +
                str(succesfully) +
                ' have passed')

        metric = nagiosplugin.Metric(
            'Failed protection runs',
            fail,
            min=0,
            context='failures')
        return metric

    def epoch_to_date(self, epoch):
        """
        Method to convert epoch time in usec to date format
        :param epoch(int): Epoch time of the job run.
        :return: date(str): Date format of the job runj.
        """
        date = datetime.datetime.fromtimestamp(epoch / 10**6)
        return date


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
        help='return critical if occupancy is outside RANGE. ')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        Cohesityprotectionstatus(
            args.ip, args.user, args.password))
    check.add(
        nagiosplugin.ScalarContext(
            'failures',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
