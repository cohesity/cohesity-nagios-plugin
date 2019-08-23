

Beta Cohesity Nagios Plugin 
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
On a Linux server follow these steps to download nagios core:  
https://support.nagios.com/kb/article/nagios-core-installing-nagios-core-from-source-96.html

## Step 2 
Install Cohesity Management SDK : 
 

Install via pip:
```
pip install cohesity-management-sdk
```

Install nagios plugin library : 


 Via ```pip install nagiosplugin ```
 
* Note: use sudo install for all dependencies

## Step 3
Follow steps to add python files to nagios core plugin :
 1. Install NRPE on client VPS 
 ```apt-get install -y python nagios-nrpe-server ```
```useradd nrpe && update-rc.d nagios-nrpe-server defaults```

 2.  Add the python scripts in the directory ```/usr/local/nagios/libexec/ ```
 
 3. Make all files executable except config.py
 ```chmod +x /usr/lib/nagios/plugins/example.py```
 
 4. Add NRPE configuration 
  ```sudo vim  /usr/local/nagios/etc/objects/localhost.cfg ```
  change the following to the file command name you desire (excluding config.py)
  ```
  define service{
        use                             local-service       
        host_name                       localhost
        service_description             Check example
        check_command                   check_example
        notifications_enabled           1
        }
  ```
  
 5. Configure commands 
 ```sudo vim /usr/local/nagios/etc/objects/commands.cfg```
 change the following to the file names and command names, excluding config.py
 
 ``` 
 define command{
 command_name    example.py 
 command_line    $USER1$/example.py 
 }
 ```
 
 6. Verify configuration ```/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg ```
 
 7. restart service ```service nagios restart```

Note:
  * To run scripts on nagios UI and terminal ensure to initialize the information by editing the config.py script (ip, user, password, domain)
  ```
        self.ip = ip
        self.user = user
        self.password = password
        self.domain = domain
                                              
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
