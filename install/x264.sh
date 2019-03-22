#!/bin/bash

set -e
if [ -d "x264" ]; then
  cd x264
  git pull
  make distclean
else
  git clone http://git.videolan.org/git/x264.git
  cd x264
fi
./configure --enable-shared
make -j4
sudo make install
cd ..
