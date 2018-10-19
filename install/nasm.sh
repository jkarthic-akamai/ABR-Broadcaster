#!/bin/bash

set -e

if nasm -v; then
  echo "Found nasm";
else
  echo "Installing nasm";
  if [ -d "nasm-2.13.03" ]; then
    rm -rf nasm-2.13.03
  fi
  curl -O https://www.nasm.us/pub/nasm/releasebuilds/2.13.03/nasm-2.13.03.tar.bz2
  tar -xvjf nasm-2.13.03.tar.bz2
  rm nasm-2.13.03.tar.bz2
  cd nasm-2.13.03
  ./configure --prefix=/usr/local
  make -j4
  sudo make install
  cd ..
fi
