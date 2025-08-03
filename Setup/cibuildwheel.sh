
python -m venv venv-cibuildwheel
. venv-cibuildwheel/bin/activate
pip install cibuildwheel

cibuildwheel --platform linux

