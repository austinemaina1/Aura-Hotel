#!/bin/bash
set -e

echo "Using python: $(which python3)"
python3 -m venv /tmp/build_venv
source /tmp/build_venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate