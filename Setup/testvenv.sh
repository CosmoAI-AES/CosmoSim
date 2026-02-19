# (C) 2025: Hans Georg Schaathun <hg@schaathun.net>

mkdir -p venv
python -m venv venv/test
. venv/test/bin/activate

sh Setup/build.sh

pip install -r requirements.txt
pip install -e .
