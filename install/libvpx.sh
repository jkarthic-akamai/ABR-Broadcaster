#!/bin/bash

set -e
if [ -d "libvpx" ]; then
  cd libvpx
  git pull
  make distclean
else
  git clone https://chromium.googlesource.com/webm/libvpx/
  cd libvpx
fi
./configure
make -j4
sudo make install
cd ..
