#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Christina Mudarth <christina.mudarth@cohesity.com>
# This script is used to monitor the backup and copy runs in the last n days, n passed as an argument to the script.
# The status is
#        OK - if the number of failed backup + copy runs are within the warning and critical thresholds
#        WARNING - if the number of failed backup + copy runs are above the warning threshold
#        and below the critical threshold
#        CRITICAL - if the number of failed backup runs are above the critical threshold
# The default warning and critical threshold is 0
# Usage :
# python check_cohesity_protection_runs.py --cluster_vip 10.10.99.100 --host_name PaulCluster
#                                               --auth_file /abc/def/config.ini -w 60 -c 90
#

import argparse
import datetime
import logging
import time
import nagiosplugin
import configparser
from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.status_backup_run_enum import StatusBackupRunEnum
from cohesity_management_sdk.models.status_copy_run_enum import StatusCopyRunEnum

_log = logging.getLogger('nagiosplugin')


class CohesityProtectionStatus(nagiosplugin.Resource):
    def __init__(self, args):
        """
        Method to initialize
        :param args: commandline arguments
        """
        parser = configparser.ConfigParser()
        parser.read(args.auth_file)
        self.cohesity_client = CohesityClient(cluster_vip=args.cluster_vip,
                                              username=parser.get(
                                                  args.host_name, 'username'),
                                              password=parser.get(
                                                  args.host_name, 'password'),
                                              domain=parser.get(args.host_name, 'domain'))
        self.args = args
        self.SECONDS_TO_MICROSECONDS = 1000000
        self.SECONDS_IN_DAY = 86400
        self.NUMBER_OF_RUNS = 1000000000000

    @property
    def name(self):
        return 'COHESITY_PROTECTION_RUN_STATUS'

    def failed_backup_runs(self):
        """
        Method to get the protection run status
        :return: number of passed and failed protection runs
        """
        try:
            # current timestamp in microseconds
            end_time_usecs = int(time.time() * self.SECONDS_TO_MICROSECONDS)

            # start timestamp in microseconds
            start_time_usecs = int((time.time() - int(self.args.days) *
                                    self.SECONDS_IN_DAY) * self.SECONDS_TO_MICROSECONDS)
            protection_runs_list = self.cohesity_client.\
                protection_runs.get_protection_runs(start_time_usecs=start_time_usecs,
                                                    end_time_usecs=end_time_usecs,
                                                    num_runs=self.NUMBER_OF_RUNS)
        except APIException as e:
            _log.debug("get protection runs APIException raised: " + e)
        failed_backup_runs = []
        failed_copy_runs = []

        for protection_runs in protection_runs_list:
            if protection_runs.job_name.startswith("_DELETED"):
                continue
            try:
                if protection_runs.backup_run.status == (
                        StatusBackupRunEnum.KFAILURE):
                    backup_run_details = 'Job Name: ' + protection_runs.job_name + \
                        ' Type: Backup run' + \
                        ', Error: ' + protection_runs.backup_run.error
                    failed_backup_runs.append(backup_run_details)
                if len(protection_runs.copy_run) > 1:
                    for protection_copy_run in protection_runs.copy_run[1:]:
                        if protection_copy_run.status == StatusCopyRunEnum.KFAILURE:
                            copy_run_details = 'Job Name: ' + protection_runs.job_name + \
                                               ' Type: Copy run' + \
                                               ', Error: ' + protection_copy_run.error
                            failed_copy_runs.append(copy_run_details)
                            break
            except TypeError as e:
                print("Error" + str(e))
        return [failed_backup_runs, failed_copy_runs]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        failed_runs = self.failed_backup_runs()
        if len(failed_runs[0]) + len(failed_runs[1]) == 0:
            _log.info(
                "Cluster ip = {}: ".format(self.args.cluster_vip) +
                "In the past " + str(self.args.days) + " days, there are no backup/copy run failures")
        else:
            _log.info(
                "Cluster ip = {}: ".format(self.args.cluster_vip) +
                "In the past " + str(self.args.days) + " days, there are " + str(len(failed_runs[0])) +
                " backup run failures and " + str(len(failed_runs[1])) + " copy run failures")
            for backup_run in failed_runs[0][0:5]:
                _log.info(backup_run)

            for copy_run in failed_runs[1][0:5]:
                _log.info(copy_run)

        metric = nagiosplugin.Metric(
            "Failed backup/copy runs",
            len(failed_runs[0]) + len(failed_runs[1]),
            min=0,
            context='failed_runs')
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
    argp.add_argument('-ip', '--cluster_vip', required=True,
                      help='Cohesity cluster ip or FQDN')
    argp.add_argument('-n', '--host_name', required=True,
                      help='Host name configured in Nagios')
    argp.add_argument('-f', '--auth_file', required=True,
                      help='.ini file path with Cohesity cluster credentials')
    argp.add_argument('-d', '--days', default=1,
                      help='The number of days of protection runs to monitor')
    argp.add_argument('-w', '--warning', metavar='RANGE', default='~:0', help='return warning if'
                                                                              ' occupancy is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='~:0', help='return critical if'
                                                                               ' occupancy is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output'
                                                                         ' verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(
        CohesityProtectionStatus(args))
    check.add(
        nagiosplugin.ScalarContext(
            'failed_runs',
            args.warning,
            args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
