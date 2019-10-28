#!/bin/sh

python -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
python -m unittest discover --start-directory tests
