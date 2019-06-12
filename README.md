

Cohesity Nagios Plugin
=================

## Overview

The *Cohesity Nagios Plugin*  provides an easy-to-use plugin to perform checks and recieve notifications from a Cohesity cluster. 


## Install

Install via git:
```
git clone https://github.com/cohesity/cohesity-nagios-plugin.git
```


## How to Use:

Initializing the Client:
```
username = 'Username'
password = 'Password'
domain = 'Domain' #optional
cluster_vip = 'prod-cluster.eng.cohesity.com'
client = CohesityClient(cluster_vip, username, password, domain)
```

## You can perform a wide range of operations such as:
* Check general alerts 
* Check protection policy runs in the past day
* Check cluster health 
* Check storage
* Check node status 
* Check percent of objects protected 
* Check metadata storage 
* Check recoveries in the past 30 days 
