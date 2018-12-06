#!/bin/bash

set -e
set -o pipefail
work_dir=`pwd`
if ! grep -q $work_dir $1; then
  sed "s|<working directory>|$work_dir|" < install/directory.conf | sudo tee -a $1
fi
if ! grep -q $work_dir $2; then
  sed "s|<working directory>|$work_dir|" < install/vhost.conf | sudo tee -a $2
fi
# Add read + execute permissions to all parent directories
while [[ $work_dir != / ]]; do sudo chmod a+rx "$work_dir"; work_dir=$(dirname "$work_dir"); done;