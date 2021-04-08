#!/bin/bash
IP=`ifconfig -a | grep "inet" | grep -v 127.0.0.1 | grep -v "inet6" | awk '{print $2}'`
HOST_IP=${SERVER_IP_ADDR}
HOST_PORT=${SERVER_PORT}
sed -i "s/{SERVER_IP_ADDR}/$IP/g" /etc/apache2/sites-available/httppool_server.conf
sed -i "s/{SERVER_PORT}/${HOST_PORT}/g" /etc/apache2/sites-available/httppool_server.conf
echo ===== /etc/apache2/sites-available/httppool_server.conf
grep Virtual /etc/apache2/sites-available/httppool_server.conf
grep ServerName /etc/apache2/sites-available/httppool_server.conf

mv /etc/apache2/apache2.conf /etc/apache2/apache2.conf.bk \
&& grep -i -v ServerName  /etc/apache2/apache2.conf.bk \
| sed -e "s/^#.*Global configuration.*$/&\n\nServerName $IP\n/" >\
/etc/apache2/apache2.conf

echo ===== /etc/apache2/apache2.conf
grep -i ServerName

sed -i "s/^Listen .*/Listen ${HOST_PORT}/g" /etc/apache2/ports.conf
echo ===== /etc/apache2/ports.conf
grep Listen /etc/apache2/ports.conf

sed -i "s/^EXTHOST =.*$/EXTHOST = \'$IP\'\n/g" \
    -i "s/^EXTPORT =.*$/EXTPORT = $HOST_PORT\n/g" \
    -i "s/^conf\s*=\s*.*$/conf = 'external'\n/g" .config/pnslocal.py

echo =====  .config/pnslocal.py
grep ^conf  .config/pnslocal.py
grep ^EXHOST  .config/pnslocal.py
grep ^EXPORT  .config/pnslocal.py