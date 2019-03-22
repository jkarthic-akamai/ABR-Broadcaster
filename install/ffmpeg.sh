#!/bin/bash

set -e
if [ -d "ffmpeg" ]; then
	cd ffmpeg
	git pull
	make distclean
else
	git clone https://git.ffmpeg.org/ffmpeg.git
	cd ffmpeg
fi
./configure --enable-libx264 --enable-libvpx --enable-gpl $1
make -j4
sudo make install
cd ..
