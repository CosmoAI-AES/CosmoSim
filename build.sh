#! /bin/sh
# (C) 2025: Hans Georg Schaathun <georg@schaathun.net> 

# Build script

. pythonenv/bin/activate

rm -rf build

conan install . --output-folder=build --build=missing


cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=build/Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release

cmake --build .

# mkdir -p bin lib 
# cmake --install build --prefix .
