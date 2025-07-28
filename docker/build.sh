#! /bin/sh
# (C) 2025: Hans Georg Schaathun <georg@schaathun.net> 

# Build script
# As of 28 July 2025, this script works on Ubuntu 22.04 and Debian.
# It does not work on Ubuntu 24.04


. /pythonenv/bin/activate

cd /CosmoSim

rm -rf build

conan profile detect
conan install . --output-folder=build --build=missing --profile:build=conan2/linux-profile --profile:host=conan2/linux-profile


( cd build && \
  cmake .. -DCMAKE_TOOLCHAIN_FILE=build/Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release && \
  cmake --build .
)

