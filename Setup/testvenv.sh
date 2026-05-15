# (C) 2025: Hans Georg Schaathun <hg@schaathun.net>

D=/tmp/venv/test

mkdir -p $D

if test -r $D/bin/activate
then
   . $D/bin/activate
else
   mkdir -p venv
   python -m venv $D
   . $D/bin/activate

   sh Setup/build.sh

   pip install jupytext jupyterlab toml
   pip install -e .
fi
