#!/bin/sh
# (C) 2022,2025: Hans Georg Schaathun <georg@schaathun.net> 

# Build scripts for NTNU's IDUN cluster.

module purge
module load OpenCV/4.8.0-foss-2022b-contrib
module load SymEngine/0.11.2-gfbf-2022b
module load CMake/3.24.3-GCCcore-12.2.0
module load SciPy-bundle/2023.02-gfbf-2022b

module list

rm -rf build
mkdir build
cmake . -B build
cmake --build build

mkdir -p bin lib 
cmake --install build --prefix .
