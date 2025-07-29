# (C) 2025: Hans Georg Schaathun <hg@schaathun.net>

mkdir -p venv
python -m venv venv/build
. pythonenv/bin/activate
pip install -r requirements-build.txt
