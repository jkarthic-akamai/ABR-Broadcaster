#!/bin/bash

set -e
install/others_ubuntu.sh
install/nasm.sh
install/x264.sh
install/ffmpeg.sh
install/abr_broadcaster.sh
install/apache_config.sh /etc/apache2/apache2.conf /etc/apache2/sites-enabled/000-default.conf
sudo service apache2 reload
