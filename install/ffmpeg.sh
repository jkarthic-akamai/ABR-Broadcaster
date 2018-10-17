#!/bin/bash

if [ -d "ffmpeg" ]; then
	cd ffmpeg
	git pull
else
	git clone https://git.ffmpeg.org/ffmpeg.git
	cd ffmpeg
fi
./configure --enable-libx264 --enable-gpl $1
make -j4
sudo make install
cd ..
