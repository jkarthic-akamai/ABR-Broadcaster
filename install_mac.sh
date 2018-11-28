#!/bin/bash

set -e
install/others_mac.sh
install/nasm.sh
install/x264.sh
install/libvpx.sh
install/ffmpeg.sh
install/abr_broadcaster.sh
install/apache_config_mac.sh
install/apache_config.sh /etc/apache2/httpd.conf /etc/apache2/extra/httpd-vhosts.conf
sudo apachectl restart
