#!/bin/bash
set -e

echo "Using python: $(which python3)"
python3 -m pip install --break-system-packages --upgrade pip
python3 -m pip install --break-system-packages -r requirements.txt

python3 manage.py collectstatic --noinput
python3 manage.py migrate