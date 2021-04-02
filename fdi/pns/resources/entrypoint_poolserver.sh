#!/bin/bash
IP=`ifconfig -a | grep "inet" | grep -v 127.0.0.1 | grep -v "inet6" | awk '{print $2}'`
HOST_IP=B_IP
HOST_PORT=B_PO
sed -i "s/{SERVER_IP_ADDR}/$IP/g" /etc/apache2/sites-available/poolserver.conf
sed -i "s/{SERVER_PORT}/${HOST_PORT}/g" /etc/apache2/sites-available/poolserver.conf
echo ===== /etc/apache2/sites-available/poolserver.conf
grep Virtual /etc/apache2/sites-available/poolserver.conf
grep ServerName /etc/apache2/sites-available/poolserver.conf

sed -i "s/Listen 80/Listen ${HOST_PORT}/g" /etc/apache2/ports.conf
echo ===== /etc/apache2/ports.conf
grep Listen /etc/apache2/ports.conf

cat << EOC >>  .config/pnslocal.py
# auto-generated by entrypoint.sh to override above. DO not edit
pnsconfig['node'] = {'username': 'foo', 'password': 'bar', 
                     'host': '${HOST_IP}', 'port': ${HOST_PORT}}
pnsconfig['base_poolpath'] = '/'
pnsconfig['server_poolpath'] = '/data'
pnsconfig['serveruser'] = 'apache'
pnsconfig['ptsuser'] = 'apache'

logger.warn('*******')
EOC
echo =====  .config/pnslocal.py
tail -8 .config/pnslocal.py