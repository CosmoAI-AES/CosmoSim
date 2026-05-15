# (C) 2025: Hans Georg Schaathun <hg@schaathun.net>

if test -r venv/run/bin/activate
then
   . venv/run/bin/activate
else
   mkdir -p venv
   python -m venv venv/run
   . venv/run/bin/activate
   pip install -r requirements.txt
fi
