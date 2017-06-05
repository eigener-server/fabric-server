### Quick start of the Hedgehog Cloud
Hedgehog Cloud: Nexcloud, Lektor, Wordpress, Letsencrypt, ... running with docker-compose ... setting up the server with fabric
https://github.com/eigener-server/docker-compose

```
mkdir /srv/fabric
cd /srv/fabric
wget https://raw.githubusercontent.com/eigener-server/fabric-server/master/fabfile.py
```
```
vi fabfile.py # Change Server IP, Your eMail Address, Your Domain, ...
```
```
fab -H root@150.60.70.80 --password nZZGSZW67689 remote new_server
fab -H demo@150.60.70.80 --password gdgwdbchwenZZGSZW67689 remote_sudo new_server_root_password
fab -H demo@150.60.70.80 --password gdgwdbchwenZZGSZW67689 remote_sudo docker
fab -H demo@150.60.70.80 --password gdgwdbchwenZZGSZW67689 remote_sudo docker_compose
```

[Next Step](https://github.com/eigener-server/docker-compose)

[Howto](https://www.eigener-server.ch/en/igel-cloud)

### Parts of the Hedgehog cloud
* nextcloud www.nextcloud.com
* lektor with admin panel www.getlektor.com
* apache servs your Lektor homepage
* haproxy
* mariadb
* redis
* letsencrypt for certificates
* wordpress as alternative for lektor

### License of the Hedgehog Cloud

You may duplicate and redistribute the material in any format or medium as well as refix, alter, and build
upon the material for any purpose, even commercially.


The following conditions must be observed:
Attribution — You must provide a link to our website (www.eigener-server.ch/en/igel-cloud) on your website
Website. We prefer the footer.

Removing the link — We understand that there are situations where you do not want to use a link reference.
If that is your case, then you can transfer us a usage fee of 10 CHF by Paypal. This allows you to use the
hedgehog cloud free of charge on a domain.

You can send your payments via Paypal to the following address: igel-cloud@nextora.ch
Please note the URL of the website, where the hedgehog cloud is used, as a remark with the Paypal Payment.
Keep your Paypal receipt as proof of payment.

![Creative Commons Lizenzvertrag](https://i.creativecommons.org/l/by/4.0/80x15.png)

Hedgehog Cloud by [www.eigener-server.ch](https://www.eigener-server.ch/en/igel-cloud)  is licensed under a [Creative Commons Namensnennung 4.0 International Lizenz](href="http://creativecommons.org/licenses/by/4.0/).


### Information for Nextcloud
Please set up your domain to access your Nextcloud (https://yourdomain.ch). 
'''
    - NEXTCLOUD_DOMAIN=eigener-server.ch
'''
In case you are comnnecting to the IP of the server (https://192.168.1.79) set your Domain with the IP.
'''
    - NEXTCLOUD_DOMAIN=192.168.1.97
'''

Depending on the system it could take up to two minutes until everything ist up.
'''
'docker logs $(docker ps | grep _nextcloud_1 | awk "{print \$1}")' shows:
'SQLSTATE[HY000] [2002] Connection refused' until mariadb is running
'Nextcloud is not installed' during the nextcloud setup
'Command line: /usr/sbin/apache2 -D FOREGROUND' after nextcloud is running
'''

### Information for HAPROXY
Please set up the IP of your notebook / home network. In case you connect via public IP then the public IP 
of your router is needed to connect to the admin Panel from haproxy and the admin panel from lektor.

You could for a test setup also use '0.0.0.0/0' to allow everything. Be carefull because this is not secure.

'''
    - HAPROXY_ADMIN_USER_IP=192.168.1.0/24
'''

### Version Control

1.1.1 Version Format

1     The first digit will count up if a major Version of the source changes for example PHP Version 7.0 to 7.1 or
Nextcloud Version 11 to 12 or the structure from the host directory changes.
1.1   The second digit will count up if the new setup might affect your system / should be tested by you after update.
1.1.1 The third digit will count up for small changes / small update of the source. Should not impact your system.

### Release Management

1.0.0 First productive release
0.x.x Development release

### FAQ
Can I be sure that the Version on Github is the same as on Docker?
*Yes. Docker is set up for automatic build. After a new Version is pushed to github docker will be informed from github
and does a pull from the source and generates the Image*

