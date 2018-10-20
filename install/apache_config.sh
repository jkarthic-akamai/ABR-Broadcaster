#!/bin/bash

set -e
set -o pipefail
work_dir=`pwd`
sed "s|<working directory>|$work_dir|" < install/directory.conf | sudo tee -a $1
sed "s|<working directory>|$work_dir|" < install/vhost.conf | sudo tee -a $2
