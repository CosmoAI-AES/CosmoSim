#! /bin/sh
# (C) 2022: Hans Georg Schaathun <georg@schaathun.net> 

# Build script

. pythonenv/bin/activate

rm -rf build

## if /bin/true
## then
   conan install . -s build_type=Release -if build -b missing
   # conan install . -if build
   cmake . -B build -DCMAKE_BUILD_TYPE=Release
## else
##    cmake . -B build -DCMAKE_BUILD_TYPE=Release  \
##        -DCMAKE_TOOLCHAIN_FILE="$HOME/git/cosmoai/vcpkg/scripts/buildsystems/vcpkg.cmake" \
##        -DCOSMOSIM_USE_CONAN=OFF
## fi

cmake --build build || exit 2

mkdir -p bin lib 
cmake --install build --prefix .
