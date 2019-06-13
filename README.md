

Cohesity Nagios Plugin
=================

# Overview

The *Cohesity Nagios Plugin*  provides an easy-to-use plugin to perform checks and recieve notifications from a Cohesity cluster. 


# Install

Install via git:
```
git clone https://github.com/cohesity/cohesity-nagios-plugin.git
```


# How to Use:

## Step 1
on an ubuntu server follow these steps to download nagios core: 
https://support.nagios.com/kb/article/nagios-core-installing-nagios-core-from-source-96.html#Ubuntu

## Step 2 
install Cohesity SDK : 
https://github.com/cohesity/app-sdk-python

install nagios plugin library : 
https://pypi.org/project/nagiosplugin/

* Note: use sudo install for all dependencies

## Step 3
follow steps to add python files to nagios core plugin :
https://www.digitalocean.com/community/tutorials/how-to-create-nagios-plugins-with-python-on-ubuntu-12-10

Note: 
  * In terminal to run the scripts ensure to use the following commands
  ```
  python check_cohesity_cluster_storage.py -i 'IP ADDRESS' -u 'USERNAME' -p 'PASSWORD'
  
  ```
  * To run scripts on nagios UI ensure to initialize the information by editing the script (ip, user, password)
  ```
  self.ip = ip
        self.user = user
        self.password = password
        self.cohesity_client = CohesityClient(cluster_vip=ip,
                                              username=user,
                                              password=password,
                                              domain=DOMAIN)
                                              
  ```
 ## Step 4 :tada:
 
 Once this is done the nagios plugin should be running and giving you updates on cluster information.
 
# You can perform a wide range of operations such as:
* Check general alerts 
* Check protection policy runs in the past day
* Check cluster health 
* Check storage
* Check node status 
* Check percent of objects protected 
* Check metadata storage 
* Check recoveries in the past 30 days 
