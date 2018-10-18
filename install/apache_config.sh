#!/bin/bash

set -e
set -o pipefail
work_dir=`pwd`
sed "s|<working directory>|$work_dir|" < install/directory.conf | sudo tee -a /etc/apache2/apache2.conf
sed "s|<working directory>|$work_dir|" < install/vhost.conf | sudo tee -a /etc/apache2/sites-enabled/000-default.conf
sudo service apache2 reload
