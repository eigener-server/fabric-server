import os
from fabric.api import sudo, local, run, cd, settings
from fabric.contrib.files import exists, sed, append, uncomment, comment, contains
from fabric.operations import put
from fabric.state import env
from fabric.context_managers import shell_env

new_user = 'demo'
new_user_password = 'gdgwdbchwenZZGSZW67689'
new_root_user_password = 'gdgwdbchwenZZGSZW67689'

outgoing_mail_password = 'mail.eigener-server.ch:alarm@eigener-server.ch:password1234'
outgoing_mail_address = 'alarm@eigener-server.ch'
outgoing_mail_server_name = 'dev001.eigener-server.ch'
outgoing_mail_relay = 'mail.eigener-server.ch'

server_hostname = 'dev001'
server_fqdn = 'dev001.eigener-server.ch'
server_ip_address = '150.60.70.80'



def remote():
    env.run = run
    env.use_sudo = False
    #env.hosts = [server_ip_address]

def remote_sudo():
    env.run = sudo
    env.use_sudo = True
    #env.hosts = [server_ip_address]

def update_repositories():
    env.run('apt-get update')

def upgrade_repositories():
    env.run('apt-get upgrade')

def dist_upgrade_repositories():
    env.run('apt-get dist-upgrade')

def change_config_file(filename, parameter, value, delimiter):
        sed(filename, 
                r'^[ #]*%s[\s\t =:]+.*' % parameter, 
                '%s%s%s' % (parameter, delimiter, value),
                use_sudo=False)
        append(filename,
                '%s%s%s' % (parameter, delimiter, value),
                use_sudo=False)

def apt_cron():
    env.run('apt-get install -y cron-apt')
    env.run('sed -n "/security/p" /etc/apt/sources.list > /etc/apt/security-sources.list')
    change_config_file('/etc/cron-apt/config', 'MAILTO', '"root"', '=')
    change_config_file('/etc/cron-apt/config', 'MAILON', '"upgrade"', '=')
    change_config_file('/etc/cron-apt/config', 'OPTIONS', '"-q -d -o Dir::Etc::SourceList=/etc/apt/security-sources.list"', '=')

def apt_exim4():
    env.run('echo "exim4-config    exim4/mailname  string  ' + outgoing_mail_server_name + '" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_eximconfig_configtype  select  mail sent by smarthost; no local mail" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_local_interfaces       string  127.0.0.1 ; ::1" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_other_hostnames        string" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_relay_domains  string" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_relay_nets     string" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_smarthost      string  ' + outgoing_mail_relay + '" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/hide_mailname     boolean true" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/use_split_config  boolean false" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_minimaldns     boolean false" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_readhost       string" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/no_config boolean true" | debconf-set-selections')
    env.run('echo "exim4-config    exim4/dc_postmaster     string  ' + new_user + '" | debconf-set-selections')
    env.run('apt-get install -y exim4')
    append('/etc/exim4/passwd.client', outgoing_mail_password)
    change_config_file('/etc/aliases', 'root', outgoing_mail_address, ': ')
    change_config_file('/etc/aliases', new_user, outgoing_mail_address, ': ')
    env.run('service exim4 restart')

def geoip_iptables():
    env.run('apt-get -y install iptables-dev xtables-addons-common')
    env.run('apt-get -y install libtext-csv-xs-perl')
    if not exists('/usr/share/xt_geoip'):
        env.run('mkdir -p /usr/share/xt_geoip')
    with cd('/usr/lib/xtables-addons/'):
        env.run('./xt_geoip_dl')
        env.run('./xt_geoip_build -D /usr/share/xt_geoip *.csv')

    with settings(warn_only=True):
        if env.run('iptables -C INPUT -i lo -j ACCEPT').failed:
            env.run('iptables -A INPUT -i lo -j ACCEPT')
        if env.run('iptables -C INPUT -p tcp --dport 22 -m geoip --source-country DE,CH -j ACCEPT').failed:
            env.run('iptables -A INPUT -p tcp --dport 22 -m geoip --source-country DE,CH -j ACCEPT')
        if env.run('iptables -C INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT').failed:
            env.run('iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT')
    env.run('iptables -P INPUT DROP')
    env.run('ip6tables -P INPUT DROP')

    env.run('echo "iptables-persistent iptables-persistent/autosave_v4 boolean true" | debconf-set-selections')
    env.run('echo "iptables-persistent iptables-persistent/autosave_v6 boolean true" | debconf-set-selections')
    env.run('apt-get -y install iptables-persistent')

    append('/etc/geoIPupdateIPtables ', 'bin/rm /usr/lib/xtables-addons/GeoIPv6.csv')
    append('/etc/geoIPupdateIPtables ', '/usr/lib/xtables-addons/xt_geoip_dl')
    append('/etc/geoIPupdateIPtables ', '/usr/lib/xtables-addons/xt_geoip_build -D /usr/share/xt_geoip *.csv')
    append('/etc/geoIPupdateIPtables ', '/sbin/iptables-restore < /etc/iptables/rules.v4')
    env.run('chmod +x /etc/geoIPupdateIPtables')

    with settings(warn_only=True):
        env.run('bach -c"crontab -l > /tmp/mycron"') #fails if crontab is not setup yet
    append('/tmp/mycron', '# Update geoIP Data iptables jeden ersten des Monates um 0:45')
    append('/tmp/mycron', '45 0 1 * * /etc/geoIPupdateIPtables  >> /var/log/geoIPupdate 2>&1')
    env.run('crontab /tmp/mycron')
    env.run('rm /tmp/mycron')

def apt_fail2ban():
    env.run('apt-get -y install fail2ban')
    append('/etc/fail2ban/jail.d/bantime.conf', '[DEFAULT]')
    change_config_file('/etc/fail2ban/jail.d/bantime.conf', 'bantime', '3600', ' = ')
    env.run('service fail2ban restart ')
    env.run('bash -c "iptables-save > /etc/iptables/rules.v4"')
    env.run('bash -c "ip6tables-save > /etc/iptables/rules.v6"')

def apt_git():
    env.run('apt-get install -y git')

def apt_sudo():
    env.run('apt-get -y install sudo')

def add_new_user(in_user=new_user, in_password=new_user_password):
    env.run('adduser --disabled-password --gecos "" ' + in_user)
    env.run('adduser ' + in_user + ' sudo')
    change_user_password(in_user, in_password)

def change_user_password(in_user=new_user, in_password=new_root_user_password):
    env.run('bash -c \'echo "{username}:{password}" | chpasswd\' '.format(username=in_user, password=in_password))

def hostname():
    change_config_file('/etc/hosts', '127.0.1.1', server_fqdn + ' ' + server_hostname, '      ')
    change_config_file('/etc/hosts', server_ip_address, server_fqdn + ' ' + server_hostname, '   ')
    env.run('bash -c "echo ' + server_hostname + ' > /etc/hostname"')
    env.run('hostname -F /etc/hostname')
    env.run('/etc/init.d/hostname.sh')

def secure_ssh():
    append('/etc/ssh/sshrc', 'ip=`echo $SSH_CONNECTION | cut -d " " -f 1`')
    append('/etc/ssh/sshrc', 'logger -t ssh-wrapper $USER login from $ip')
    append('/etc/ssh/sshrc', 'echo "User $USER just logged in from $ip" | mail -s "SSH Login" ' + outgoing_mail_address + ' &')
    append('/etc/ssh/banner', '!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!')
    append('/etc/ssh/banner', 'The use of this machine is restricted to authorized users only.')
    append('/etc/ssh/banner', 'All the activities on this SSH Server are logged.')
    change_config_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'no', ' ')
    change_config_file('/etc/ssh/sshd_config', 'Banner', '/etc/ssh/banner', ' ')
    change_config_file('/etc/ssh/sshd_config', 'AllowUsers', new_user, ' ' )

    sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no')
    append('/etc/ssh/sshd_config', 'Banner /etc/ssh/banner')
    env.run('service ssh restart')

def new_server_root_password():
    change_user_password("root", new_root_user_password)

def docker():
    env.run('apt-get remove -y docker docker-engine')
    env.run('apt-get install -y apt-transport-https ca-certificates curl software-properties-common')
    env.run('bash -c "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -"')
    env.run('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    update_repositories()
    env.run('apt-get install -y docker-ce')
    env.run('docker --version')

def docker_compose():
    env.run('sh -c "curl -L https://github.com/docker/compose/releases/download/1.13.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"')
    env.run('chmod +x /usr/local/bin/docker-compose')
    env.run('docker-compose --version')

def install_fabric():
    update_repositories()
    env.run('apt-get install build-essential libssl-dev libffi-dev python-dev')
    env.run('apt-get install python-pip')
    env.run('pip install --upgrade pip')
    env.run('pip install fabric')

def new_server():
    update_repositories()
    upgrade_repositories()
    dist_upgrade_repositories()
    apt_cron()
    apt_sudo()
    add_new_user()
    apt_exim4()
    geoip_iptables()
    apt_fail2ban()
    apt_git()
    hostname()
    secure_ssh()

