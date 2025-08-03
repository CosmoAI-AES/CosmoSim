#! /bin/sh
# (C) 2025: Hans Georg Schaathun <georg@schaathun.net> 

# Build script for python wheel



sh Setup/buildvenv.sh
. venv/build/bin/activate

python -m build > build-wheel.log 2>&1 &
