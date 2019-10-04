

Cohesity Nagios Plugin
===========================

## Overview

The *Cohesity Nagios Plugin*  provides an easy-to-use plugin to monitor Cohesity clusters. 

## Requirements
- Nagios Core 4.4.3+
- Python 2.7+ or 3.5+
- Python dependencies
    - argparse
    - logging
    - nagiosplugin
    - configparser
    - cohesity_management_sdk
- Cohesity 6.3.1+

## Steps to setup Nagios Core and Cohesity Nagios Plugin
1. Install Nagios Core and its associated plugins following the steps in the link <br/>
https://support.nagios.com/kb/article/nagios-core-installing-nagios-core-from-source-96.html
2. Install python and pip if not already installed
3. Download or git clone Cohesity nagios plugin scripts to any directory on your machine <br/>
`git clone https://github.com/cohesity/cohesity-nagios-plugin.git`
4. Find requirements.txt in the cloned directory and install the dependecies using the command <br/>
`pip install -r requirements.txt`
5. Copy the python scripts in src directory to */usr/local/nagios/libexec* directory
6. Make all the cohesity nagios scripts executable using the command `chmod +x /abc/def/scripts.py`. Now you can use these scripts to write commands and define hosts, services
7. The scripts accepts the cluster credentails from a .ini file. Create a .ini file with cluster authentication details.  Single or multiple clusters can be monitored by defining a host for each cluster with cluster ip as host address, hostname and other host details. Put each cluster credentails in the .ini file in the following format
```ini
[Cluster1HostName]
username=abc
password=asdf
domain=LOCAL

[Cluster2HostName]
username=def
password=qwerty
domain=LOCAL
``` 
Cluster1HostName and Cluster2HostName are the host names defined in the nagios host for each cluster. Check below sections for sample hosts, services, and commands definitions <br/>

8. Add hosts, services and commands definitions to any .cfg file of your choice and include the path to these .cfg file/s in nagios.cfg in */usr/local/nagios/etc*. (Usually configuration(.cfg) files with hosts, services, commands definitions can be found in */usr/local/nagios/etc/objects* directory)
9. Verify your nagios configuration using the following command. If there are no errors continue with next steps or resolve the errors to proceed
```/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg```
10. Restart nagios service


## Scripts

### Common Arguments
1. --cluster_vip or -ip: Cohesity cluster vip or FQDN. **Required**
2. --host_name or -n: The host name given in host definition of a cluster. **Required**
3. --auth_file or -f: .ini file with cluster credentails. **Required**

### check_cohesity_alerts.py

This script gets the alerts on Cohesity cluster and nagios status is decided based on the number of critical/warning alerts. Alerts related to specific category can be monitored by passing the in the alert category in the commandline arguments <br/>
The status is <br/>
     - OK when there are zero critical and zero warning alerts <br/>
     - CRITICAL when number of critical alerts is non zero <br/>
     - WARNING when number of critical alerts is zero and warning alerts is non zero <br/>
Along with common arguments, this script accepts
- --alert or -a: The alert category. Defaults to all the alert categories. **Optional**

 Usage :
 ```
 python check_cohesity_alerts.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini --alert Disk -vv
```
 If you want alerts of specific category, pass one of the categories listed below in the command line arguments.
 If alert category is not passed, all category alerts are used to get the nagios status <br/>

 Here are the different types of categories 
   - Disk - Alerts that are related to Disk.
   - Node - Alerts that are related to Node.
   - Cluster - Alerts that are related to Cluster.
   - NodeHealth - Alerts that are related to Node Health.
   - ClusterHealth - Alerts that are related to Cluster Health.
   - BackupRestore - Alerts that are related to Backup/Restore.
   - Encryption - Alerts that are related to Encryption.
   - ArchivalRestore - Alerts that are related to Archival/Restore.
   - RemoteReplication - Alerts that are related to Remote Replication.
   - Quota - Alerts that are related to Quota.
   - License - Alerts that are related to License.
   - HeliosProActiveWellness - Alerts that are related to Helios ProActive Wellness.
   - HeliosAnalyticsJobs - Alerts that are related to Helios Analytics Jobs.
   - HeliosSignatureJobs - Alerts that are related to Helios Signature Jobs.
   - Security - Alerts that are related to Security.

### check_cohesity_metastorage.py

 This script is used to monitor the percentage of storage used for metadata
 over the total storage available for metadata on Cohesity cluster <br/>
 Along with common arguments, this script accepts
 - --warning or -w: Warning threshold. Defaults to '~:60'. **Optional**
 - --critical or -c: Critical theshold. Defaults to '~:80'. **Optional**

 Usage :
 ```
 python check_cohesity_metastorage.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini -w 60 -c 90
```
### check_cohesity_node_status.py
This script is used to find number of active nodes on a Cohesity cluster and status is <br/>
  - OK - if number of inactive nodes is zero
  - CRITICAL - if the number if inactive nodes is non zero

 Usage :
 ```
 python check_cohesity_node_status.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini
```
### check_cohesity_objects_unprotected.py

This script is used to monitor the percentage of unprotected objects on Cohesity cluster. Ths status is <br/>
  - OK - if the percentage of unprotected objects are within the warning threshold
  - WARNING - if the percentage of unprotected objects are is above the warning threshold

Along with common arguments, this script accepts
 - --warning or -w: Warning threshold. Defaults to '~:90'. **Optional**

 Usage :
 ```
 python check_cohesity_objects_unprotected.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini -w 60
```
### check_cohesity_protection_runs.py

 This script is used to monitor the backup and copy runs in the last n days, n passed as an argument to the script.
 The status is <br/>
   - OK - if the number of failed backup + copy runs are within the warning and critical thresholds
   - WARNING - if the number of failed backup + copy runs are above the warning threshold
        and below the critical threshold
   - CRITICAL - if the number of failed backup runs are above the critical threshold 

 Along with common arguments, this script accepts
 - --warning or -w: Warning threshold. Defaults to '~:0'. **Optional**
 - --critical or -c: Critical theshold. Defaults to '~:0'. **Optional**
 - --days or -d: The number of days of protection runs to moniter. Defaults to 1 day. **Optional**

 Usage :
 ```
 python check_cohesity_protection_runs.py --cluster_vip 10.10.99.100 --host_name PaulCluster --auth_file /abc/def/config.ini -w 60 -c 90
```
### check_cohesity_storage.py

 This script is used to monitor percentage of total storage used <br/>
 - used_capacity: The total capacity used, as computed by the Cohesity Cluster, after the size of the data has been
 reduced by change-block tracking, compression and deduplication
 - total_capacity: The total physical capacity in bytes as computed by the Cohesity Cluster

   `percent used =  (used_capacity/total_capacity) * 100`

Along with common arguments, this script accepts
 - --warning or -w: Warning threshold. Defaults to '~:60'. **Optional**
 - --critical or -c: Critical theshold. Defaults to '~:80'. **Optional**

 Usage :
 ```
 python check_cohesity_storage.py --cluster_vip 10.10.99.100 --host_name PaulCluster
                                              --auth_file /abc/def/config.ini -w 60 -c 90
```


## Examples:

The macros used in the examples:
- $HOSTADDRESS$ : Cluster vip or FQDN from hosts definition
- $HOSTNAME$ : Host name from hosts definition
- $USER2$ : path to .ini file with authentication details. Defined in resource.cfg
- $USER1$ : path to directory with cohesity nagios scripts. Defined in resource.cfg (for example */usr/local/nagios/libexec*)

### Commands:
```
define command{
        command_name    check_cohesity_metastorage
        command_line    $USER1$/check_cohesity_metastorage.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$ -w 60 -c 80
        }

define command{
        command_name    check_cohesity_alerts
        command_line    $USER1$/check_cohesity_alerts.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$
        }
define command{
        command_name    check_cohesity_nodes_status
        command_line    $USER1$/check_cohesity_node_status.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$
        }
define command{
        command_name    check_cohesity_unprotected_objects
        command_line    $USER1$/check_cohesity_objects_unprotected.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$ -w 80
        }
define command{
        command_name    check_cohesity_protection_runs
        command_line    $USER1$/check_cohesity_protection_runs.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$
        }
define command{
        command_name    check_cohesity_storage
        command_line    $USER1$/check_cohesity_storage.py --cluster_vip $HOSTADDRESS$ --host_name $HOSTNAME$ --auth_file $USER2$ -w 60 -c 80
        }

```

### Hosts
```
define host {
    use                     linux-server            ; Name of host template to use
                                                    ; This host definition will inherit all variables that are defined
                                                    ; in (or inherited by) the linux-server host template definition.
    host_name               Cluster1HostName
    alias                   Cluster1
    address                 10.222.22.12
}


define host {
  
    use                     linux-server            ; Name of host template to use
                                                    ; This host definition will inherit all variables that are defined
                                                    ; in (or inherited by) the linux-server host template definition.
    host_name               Cluster2HostName
    alias                   Cluster2
    address                 10.23.15.19
}
```

### Services

```
define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             META_STORAGE
        check_command                   check_cohesity_metastorage
        notifications_enabled           1
        }

define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             ALERTS
        check_command                   check_cohesity_alerts
        notifications_enabled           1
        }

define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             NODE_STATUS
        check_command                   check_cohesity_nodes_status
        notifications_enabled           1
        }

define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             OBJECTS_UNPROTECTED
        check_command                   check_cohesity_unprotected_objects
        notifications_enabled           1
        }

define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             PROTECTION_RUNS
        check_command                   check_cohesity_protection_runs
        notifications_enabled           1
        }

define service{
        use                             local-service
        host_name                       Cluster1HostName,Cluster2HostName
        service_description             STORAGE
        check_command                   check_cohesity_storage
        notifications_enabled           1
        }
```

### Auth file
config.ini

```
[Cluster1HostName]
username=paul
password=def
domain=LOCAL

[Cluster2HostName]
username=adam
password=abc
domain=LOCAL
```