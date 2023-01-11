# (C) 2022: Hans Georg Schaathun <georg@schaathun.net> 

# Build scripts for NTNU's IDUN cluster.

rm -rf build
conan install . -if build
cmake . -B build
cmake --build build

mkdir -p bin lib 
cmake --install build --prefix .
