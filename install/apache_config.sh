#!/bin/bash

set -e
set -o pipefail
work_dir=`pwd`
sed "s|<working directory>|$work_dir|" < install/directory.conf | sudo tee -a $1
sed "s|<working directory>|$work_dir|" < install/vhost.conf | sudo tee -a $2
# Add read + execute permissions to all parent directories
while [[ $work_dir != / ]]; do sudo chmod a+rx "$work_dir"; work_dir=$(dirname "$work_dir"); done;