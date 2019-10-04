#!/usr/bin/env python
# Copyright 2019 Cohesity Inc.
# Author : Cohesity Developer <cohesity-api-sdks@cohesity.com>
# This script gets the alerts on Cohesity cluster and nagios status
# is decided based on the number of critical/warning alerts. Alerts related to specific category can be monitored by
# passing the in the alert category in the commandline arguments
# The status is
#     - OK when there are zero critical and zero warning alerts
#     - CRITICAL when number of critical alerts is non zero
#     - WARNING when number of critical alerts is zero and warning alerts is non zero
# Usage :
# python check_cohesity_alerts.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini
#                                 --alert Disk -vv
#
# If you want alerts of specific category, pass one of the categories listed below in the command line arguments.
# If alert category is not passed, all category alerts are used to get the nagios status
#
# Here are the different types of categories
# Disk - Alerts that are related to Disk.
# Node - Alerts that are related to Node.
# Cluster - Alerts that are related to Cluster.
# NodeHealth - Alerts that are related to Node Health.
# ClusterHealth - Alerts that are related to Cluster Health.
# BackupRestore - Alerts that are related to Backup/Restore.
# Encryption - Alerts that are related to Encryption.
# ArchivalRestore - Alerts that are related to Archival/Restore.
# RemoteReplication - Alerts that are related to Remote Replication.
# Quota - Alerts that are related to Quota.
# License - Alerts that are related to License.
# HeliosProActiveWellness - Alerts that are related to Helios ProActive Wellness.
# HeliosAnalyticsJobs - Alerts that are related to Helios Analytics Jobs.
# HeliosSignatureJobs - Alerts that are related to Helios Signature Jobs.
# Security - Alerts that are related to Security.
#


import argparse
import configparser
import datetime
import logging
import nagiosplugin

from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.exceptions.api_exception import APIException
from cohesity_management_sdk.models.alert_state_list_enum import (
    AlertStateListEnum)
from cohesity_management_sdk.models.alert_severity_list_enum import (
    AlertSeverityListEnum)
from cohesity_management_sdk.models.alert_category_list_enum import (
    AlertCategoryListEnum)


_log = logging.getLogger('nagiosplugin')


class CohesityAlerts(nagiosplugin.Resource):
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
        self.alert_category = {
            'Disk': AlertCategoryListEnum.KDISK,
            'Node': AlertCategoryListEnum.KNODE,
            'Cluster': AlertCategoryListEnum.KCLUSTER,
            'NodeHealth': AlertCategoryListEnum.KNODEHEALTH,
            'ClusterHealth': AlertCategoryListEnum.KCLUSTERHEALTH,
            'BackupRestore': AlertCategoryListEnum.KBACKUPRESTORE,
            'Encryption': AlertCategoryListEnum.KENCRYPTION,
            'ArchivalRestore': AlertCategoryListEnum.KARCHIVALRESTORE,
            'RemoteReplication': AlertCategoryListEnum.KREMOTEREPLICATION,
            'Quota': AlertCategoryListEnum.KQUOTA,
            'License': AlertCategoryListEnum.KLICENSE,
            'HeliosProActiveWellness': AlertCategoryListEnum.KHELIOSPROACTIVEWELLNESS,
            'HeliosAnalyticsJobs': AlertCategoryListEnum.KHELIOSANALYTICSJOBS,
            'HeliosSignatureJobs': AlertCategoryListEnum.KHELIOSSIGNATUREJOBS,
            'Security': AlertCategoryListEnum.KSECURITY
        }
        self.MAX_ALERTS = 1000
        self.MICROSECONDS = 10 ** 6

    @property
    def name(self):
        return 'COHESITY_ALERT_STATUS'

    def get_alerts(self):
        """
        Method to get  critical and warning alerts
        :return: list of critical and warning alerts
        """
        try:
            if self.args.alert == '':
                alerts_list = self.cohesity_client.alerts.get_alerts(
                    max_alerts=self.MAX_ALERTS, alert_state_list=AlertStateListEnum.KOPEN)
            else:
                alerts_list = self.cohesity_client.\
                    alerts.get_alerts(alert_category_list=self.alert_category[self.args.alert],
                                      max_alerts=self.MAX_ALERTS, alert_state_list=AlertStateListEnum.KOPEN)
        except APIException as e:
            _log.debug("get alerts APIException raised: " + e)

        alerts_critical = []
        alerts_warnings = []
        for r in alerts_list:
            alert_detail = "AlertCategory:" + str(r.alert_category[1:]) + \
                           ", AlertState:" + str(r.alert_state[1:]) + \
                ", Severity:" + str(r.severity[1:]) + \
                           ", OccurrenceTime: " + \
                str(self.epoch_to_date(r.latest_timestamp_usecs))
            if r.severity == AlertSeverityListEnum.KCRITICAL:
                alerts_critical.append(alert_detail)
            if r.severity == AlertSeverityListEnum.KWARNING:
                alerts_warnings.append(alert_detail)
        return [alerts_critical, alerts_warnings]

    def probe(self):
        """
        Method to get the status
        :return: metric(str): nagios status.
        """
        alerts = self.get_alerts()
        critical = alerts[0]
        warning = alerts[1]
        if len(critical) > 0 or len(warning) > 0:
            _log.info(
                "Cluster ip = {}: ".format(self.args.cluster_vip) +
                "There are {} alerts in critical".format(len(critical)) +
                " status and {} ".format(len(warning)) + "alerts in warning" +
                " status")
            for alert in critical[0:5]:
                _log.info(alert)
            for alert in warning[0:5]:
                _log.info(alert)
        else:
            _log.info(
                "Cluster ip = {}: ".format(self.args.cluster_vip) +
                "All alerts are in info status or no alerts")

        if self.args.alert == '':
            critical_metric = 'Critical Alerts'
            warning_metric = 'Warning Alerts'
        else:
            critical_metric = 'Critical ' + self.args.alert + ' Alerts'
            warning_metric = 'Warning ' + self.args.alert + ' Alerts'

        metric_critical = nagiosplugin.Metric(
            critical_metric,
            len(critical),
            min=0,
            context='critical')

        metric_warning = nagiosplugin.Metric(
            warning_metric,
            len(warning),
            min=0,
            context='warning')
        return [metric_critical, metric_warning]

    def epoch_to_date(self, epoch):
        """
        Method to convert epoch time in usec to date format
        :param epoch(int): Epoch time
        :return: date(str): Date format
        """
        date = datetime.datetime.fromtimestamp(epoch / self.MICROSECONDS).strftime('%m-%d-%Y %H:%M:%S')
        return date


def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-ip', '--cluster_vip', required=True,
                      help='Cohesity cluster ip or FQDN')
    argp.add_argument('-n', '--host_name', required=True,
                      help='Host name configured in Nagios')
    argp.add_argument('-a', '--alert',
                      default='', choices=['Disk', 'Node', 'Cluster', 'NodeHealth',
                                           'ClusterHealth', 'BackupRestore', 'Encryption',
                                           'ArchivalRestore', 'RemoteReplication',
                                           'Quota', 'License', 'HeliosProActiveWellness',
                                           'HeliosAnalyticsJobs', 'HeliosSignatureJobs', 'Security'],
                      help='Alert category to be monitored on Cohesity cluster')
    argp.add_argument('-f', '--auth_file', required=True,
                      help='.ini file path with Cohesity cluster credentials')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output'
                                                                         ' verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()


@nagiosplugin.guarded
def main():

    args = parse_args()
    check = nagiosplugin.Check(
        CohesityAlerts(args))
    check.add(
        nagiosplugin.ScalarContext(
            'critical',
            critical='~:0'
        ))
    check.add(
        nagiosplugin.ScalarContext(
            'warning',
            warning='~:0'
        ))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
