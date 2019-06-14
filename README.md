

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
On an ubuntu server follow these steps to download nagios core:  
https://support.nagios.com/kb/article/nagios-core-installing-nagios-core-from-source-96.html#Ubuntu

## Step 2 
Install Cohesity SDK : 
 

The generated code uses Python packages named requests, jsonpickle and dateutil.
You can resolve these dependencies using pip ( https://pip.pypa.io/en/stable/ ).
This SDK uses the Requests library and will work for Python ```2 >=2.7.9``` and Python ```3 >=3.4```.

  1. Invoke ```git clone https://github.com/cohesity/app-sdk-python.git```
  2. ```cd app-sdk-python```
  2. Invoke ```pip install -r requirements.txt```
  3. Install cohesity_management_package: ```python setup.py install```. 
  This will install the package in PYTHONPATH.


Install nagios plugin library : 
 Via ```pip install nagiosplugin ```
 
* Note: use sudo install for all dependencies

## Step 3
Follow steps to add python files to nagios core plugin :
 1. Install NRPE on client VPS 
 ```apt-get install -y python nagios-nrpe-server ```
```useradd nrpe && update-rc.d nagios-nrpe-server defaults```

 2.  Add the python scripts in the directory ```/usr/local/nagios/libexec/ ```
 
 3. Make files executable 
 ```chmod +x /usr/lib/nagios/plugins/example.py```
 
 4. Add NRPE configuration 
  ```sudo nano  /usr/local/nagios/etc/nagios.cfg ```
  change the following to the file name 
  ```command[example]=/usr/lib/nagios/plugins/example.sh```
  
 5. Configure commands 
 ```sudo nano /usr/local/nagios/etc/objects/commands.cfg```
 change the following to the file name 
 
 ``` define command{ command_name    example.py command_line    $USER1$/example.py } ```
 
 5. Verify configuration ```/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg ```
 
 6. restart service ```service nagios restart```

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
